import json
import uuid
from typing import Dict, Any, List, Optional
from app.core.config import settings
from app.core.logger import logger
from app.models.pitch import (
    PitchDeck,
    Slide,
    SlideType,
    InvestorCritique,
    MetricCallout,
    DeckGenerationRequest,
    DeckGenerationResponse,
)
from app.services.vector_store import vector_store_service


SYSTEM_PROMPT = """You are a Principal Venture Capitalist at a top-tier Silicon Valley venture fund (e.g. Sequoia, Benchmark, Founders Fund) and an expert pitch deck strategist.

YOUR OBJECTIVE:
Transform raw founder notes, technical descriptions, audio transcripts, or competitor links into an institutional-grade, strictly validated 10-slide pitch deck payload.

NON-NEGOTIABLE PRINCIPLES:
1. ZERO AI BUZZWORDS:
   - STRICTLY BAN filler tokens: 'revolutionary', 'game-changing', 'paradigm shift', 'disruptive', 'synergy', 'leverage', 'next-generation', 'uniquely positioned', 'harnessing the power of'.
   - If an assertion does not name an operational mechanism or verifiable quantitative metric, re-write it until it does.
2. STRICT CANONICAL 10-SLIDE FORMAT:
   You must produce EXACTLY 10 slides in this exact sequence:
   [1] Problem (clear, painful, validated problem with quantifiable impact)
   [2] Solution (precise value proposition, mechanism of action, unfair architectural advantage)
   [3] Market (TAM/SAM/SOM with bottom-up derivation, not hand-waving stats)
   [4] Product (key capabilities, data plane / architecture status)
   [5] Traction (actual milestones, MoM growth, pilots, test volume, or prototype velocity)
   [6] Business Model (unit economics, pricing model, target ACV, gross margin dynamics)
   [7] GTM (acquisition flywheels, channel distribution, developer/enterprise sales motion)
   [8] Competition (defensibility matrix, architectural moats, zero-egress/lock-in barriers)
   [9] Team (founders' technical/operational track record and domain expertise)
   [10] The Ask (target funding amount, runway extension, milestone objectives)
3. INVESTOR CRITIQUE TAGS:
   Each slide MUST include an `investor_critique` object with:
   - `strengths`: What institutional partners find compelling.
   - `red_flags`: Vulnerabilities or diligence friction points partners will grill the founder on.
   - `hard_questions`: 2-3 specific, grilling partner meeting questions.
4. METRICS & EVIDENCE:
   Extract or infer plausible financial KPIs (`MetricCallout` objects with label, value, and context).

OUTPUT FORMAT:
Return STRICT JSON adhering to the PitchDeck schema.
"""


class DeckGeneratorService:
    """Service utilizing GCP Vertex AI Gemini 2.5 to synthesize founder notes

    into validated 10-slide decks with venture partner stress-testing.
    """

    def __init__(self):
        self.project_id = settings.GCP_PROJECT_ID
        self.location = settings.VERTEX_AI_LOCATION
        self.model_name = settings.GEMINI_MODEL_NAME
        self.mock_mode = settings.MOCK_GCP_SERVICES

        if not self.mock_mode:
            try:
                import vertexai
                from vertexai.generative_models import GenerativeModel

                vertexai.init(project=self.project_id, location=self.location)
                self.model = GenerativeModel(self.model_name)
                logger.info(
                    f"Vertex AI Gemini Generator initialized with model '{self.model_name}'"
                )
            except Exception as e:
                logger.warning(
                    f"Failed to initialize live Vertex AI Gemini: {e}. Falling back to deterministic synthesizer."
                )
                self.mock_mode = True
        else:
            logger.info("Deck Generator Service initialized in MOCK / LOCAL mode.")

    async def generate_pitch_deck(
        self, request: DeckGenerationRequest
    ) -> DeckGenerationResponse:
        """Generates an investor-grade 10-slide pitch deck from founder notes."""
        logger.info(
            f"Synthesizing deck for company: '{request.company_name}', Target: {request.target_round} {request.target_amount or ''}"
        )

        # Retrieve relevant benchmark slides from AlloyDB pgvector to ground generation
        benchmarks = await vector_store_service.search_similar_slides(
            query_text=request.raw_notes[:500], top_k=3
        )

        context_blocks = []
        for b in benchmarks.matches:
            context_blocks.append(
                f"- Benchmark [{b.deck_name} - {b.slide_type}]: {b.headline} | {b.extracted_text}"
            )
        benchmark_context = "\n".join(context_blocks)

        user_prompt = f"""
FOUNDER SUBMISSION:
Company Name: {request.company_name}
Target Round: {request.target_round}
Target Ask Amount: {request.target_amount or '$2,000,000'}
Sector: {request.industry_sector or 'Fintech / Enterprise Software'}
One-Liner: {request.one_liner or ''}
Competitor URLs: {', '.join(request.competitor_urls) if request.competitor_urls else 'None provided'}

RAW FOUNDER NOTES & DATA DUMP:
\"\"\"
{request.raw_notes}
\"\"\"

GROUNDING BENCHMARK CONTEXT (RETRIEVED FROM ALLOYDB VECTOR STORE):
{benchmark_context}

INSTRUCTIONS:
Produce a complete 10-slide PitchDeck JSON object.
Ensure zero buzzwords, strong metrics, and rigorous venture partner critique for each slide.
"""

        if self.mock_mode:
            deck = self._generate_mock_deck(request)
        else:
            try:
                from vertexai.generative_models import GenerationConfig

                generation_config = GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.2,
                    max_output_tokens=4096,
                )

                response = self.model.generate_content(
                    [SYSTEM_PROMPT, user_prompt],
                    generation_config=generation_config,
                )

                data = json.loads(response.text)
                deck = PitchDeck.model_validate(data)

            except Exception as e:
                logger.error(
                    f"Gemini 2.5 generation failed: {e}. Falling back to deterministic synthesizer."
                )
                deck = self._generate_mock_deck(request)

        deck_id = f"deck_{uuid.uuid4().hex[:12]}"
        from datetime import datetime, timezone

        return DeckGenerationResponse(
            deck_id=deck_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            deck=deck,
        )

    def _generate_mock_deck(self, req: DeckGenerationRequest) -> PitchDeck:
        """Deterministic generator for offline development, tests, and demo mode."""
        company = req.company_name or "Sentient Ledger"
        ask = req.target_amount or "$2,500,000"
        round_name = req.target_round or "Seed"

        slides_data = [
            (
                1,
                SlideType.PROBLEM,
                "Instant Settlements Broke Legacy AML & Fraud Architecture",
                "Sub-second payments require sub-millisecond risk decisions.",
                [
                    "FedNow and SEPA Instant process settlement in < 3 seconds, rendering 24-hour batch AML checks obsolete.",
                    "Incumbent rule engines suffer 42% false-positive rates on high-velocity transaction flows.",
                    "Mid-tier institutions spend $3.20 in manual investigator overhead per $1.00 of actual fraud prevented.",
                ],
                [
                    MetricCallout(label="Clearing Latency Gap", value="2.8s vs 24h", context="Instant rail vs legacy check"),
                    MetricCallout(label="False Positive Rate", value="42%", context="Monolithic rule engine benchmark"),
                    MetricCallout(label="Investigation Drain", value="$3.20", context="Spent per $1.00 fraud stopped"),
                ],
                "When capital cleared in 3 business days, overnight batching worked. On instant rails, fraud decisions must execute in-switch within 8 milliseconds.",
                InvestorCritique(
                    strengths=["Regulatory mandate and FedNow adoption create undeniable urgency."],
                    red_flags=["Must prove clear differentiation from modern cloud fraud vendors like Unit21."],
                    hard_questions=["Why won't core banking incumbents bundle streaming checks directly?"]
                )
            ),
            (
                2,
                SlideType.SOLUTION,
                "In-Memory Streaming Graph Defense for Real-Time Money Movement",
                "Edge-deployed deterministic subgraph anomaly detection scoring in 6.4ms.",
                [
                    "Drop-in Rust agent running directly in bank VPCs or on-prem gateways without exporting raw customer PII.",
                    "Continuous graph neural network updates identifying coordinated synthetic identity rings before funds leave the rail.",
                    "Automated Suspicious Activity Report (SAR) drafting reducing manual investigator backlog by 78%.",
                ],
                [
                    MetricCallout(label="Inference Latency", value="6.4ms", context="P99 edge transaction scoring"),
                    MetricCallout(label="False Positive Cut", value="-64%", context="Validated on 12M historical records"),
                    MetricCallout(label="Investigator Hours Saved", value="78%", context="Automated FinCEN SAR drafting"),
                ],
                f"{company} embeds directly into the core switch, validating transactions in 6.4ms with zero external cloud egress.",
                InvestorCritique(
                    strengths=["In-VPC edge deployment eliminates banks' #1 data sovereignty objection."],
                    red_flags=["High engineering burden maintaining distributed graph state across banking nodes."],
                    hard_questions=["What hardware acceleration is required to sustain 50,000 TPS per switch?"]
                )
            ),
            (
                3,
                SlideType.MARKET,
                "A $21.4B Market Catalyst Unlocked by Global Real-Time Rails",
                "Every financial institution must replace legacy batch compliance by 2027.",
                [
                    "TAM: $21.4B Global Financial Crime and Compliance software market growing at 19.2% CAGR.",
                    "SAM: $6.8B focused on Real-Time Payment rails, Instant Remittances, and Neobanks.",
                    "SOM: $420M initial wedge targeting high-velocity US and European fintech infrastructure providers.",
                ],
                [
                    MetricCallout(label="TAM", value="$21.4B", context="Global compliance tech by 2028"),
                    MetricCallout(label="SAM", value="$6.8B", context="Instant payment rail segment"),
                    MetricCallout(label="SOM", value="$420M", context="High-velocity fintech wedge"),
                ],
                "Global regulatory deadlines for FedNow and ISO 20022 compliance make upgrading from legacy systems mandatory for 4,000+ US institutions.",
                InvestorCritique(
                    strengths=["Bottom-up derive sizing rather than hand-wavy top-down market claims."],
                    red_flags=["Regulatory fragmentation requires localized jurisdiction rules."],
                    hard_questions=["How quickly can you penetrate regional banks with 5-year legacy contracts?"]
                )
            ),
            (
                4,
                SlideType.PRODUCT,
                "Modular Data Plane: In-Switch Interceptor + Autonomous Investigator",
                "Single binary deployment with native integrations into Jack Henry and Fiserv.",
                [
                    "Interceptor SDK: Drop-in Rust agent running adjacent to ISO 8583 and ISO 20022 messaging pipelines.",
                    "Real-Time Graph Studio: Interactive fraud ring forensic mapping updated synchronously with live flows.",
                    "Compliance Copilot: Grounded LLM synthesizing alert evidence into legally compliant audit disclosures.",
                ],
                [
                    MetricCallout(label="Deployment Velocity", value="< 2 Days", context="Via pre-built Kafka & REST bridges"),
                    MetricCallout(label="Throughput", value="85,000 TPS", context="Benchmarked per cluster instance"),
                    MetricCallout(label="Pre-Built Cores", value="6 Connectors", context="Fiserv, Thought Machine, Mambu"),
                ],
                "Our product delivers immediate defense at the switch combined with an autonomous audit portal that clears backlogs.",
                InvestorCritique(
                    strengths=["Rust-based high-performance data plane creates a technical barrier to entry."],
                    red_flags=["Core banking connectors require tedious SOC2 Type II and ISO certifications."],
                    hard_questions=["How do you guarantee zero downtime during version upgrades in live switches?"]
                )
            ),
            (
                5,
                SlideType.TRACTION,
                "3 Enterprise Pilots Live, $380k In Signed Pipeline",
                "Monitoring $140M in annualized test volume with 100% SLA uptime.",
                [
                    "Signed paid pilots with 2 Series-B neobanks and 1 regional credit union.",
                    "Evaluated 4.2M live production transactions, detecting 14 coordinated fraud attacks missed by incumbent systems.",
                    "100% pilot-to-production conversion commitment upon SOC2 Type II audit completion.",
                ],
                [
                    MetricCallout(label="Pipeline ARR", value="$380k", context="3 signed LOIs with upfront commitments"),
                    MetricCallout(label="Annualized Volume", value="$140M", context="Processed across live test rails"),
                    MetricCallout(label="Precision Rate", value="98.4%", context="Zero critical false negatives"),
                ],
                "In our first 90 days of live pilot testing, we surfaced 14 coordinated mule networks that had bypassed incumbent legacy tools.",
                InvestorCritique(
                    strengths=["Demonstrated detection superiority on real customer production data."],
                    red_flags=["Volume is promising but still modest relative to Tier-1 multinational banks."],
                    hard_questions=["What is the customer churn risk if a tier-1 customer experiences an outage?"]
                )
            ),
            (
                6,
                SlideType.BUSINESS_MODEL,
                "Volume-Tiered Platform SaaS + Per-Transaction Verification Fee",
                "Predictable recurring base contracts coupled with compounding consumption upside.",
                [
                    "Base Platform Fee: $48k - $180k/year based on core connector complexity and compliance seats.",
                    "Usage Pricing: $0.0035 per transaction screened, decaying to $0.0012 at enterprise scale.",
                    "Target Account ACV: $125k blended contract value with net revenue retention target of 145%.",
                ],
                [
                    MetricCallout(label="Target ACV", value="$125k", context="Blended Year 1 Enterprise Value"),
                    MetricCallout(label="Gross Margin", value="84%", context="Due to local edge model execution"),
                    MetricCallout(label="Target NRR", value="145%", context="Expansion driven by payment volume"),
                ],
                "Our hybrid model gives CFOs predictable base pricing while capturing uncapped upside as payment transaction volumes swell.",
                InvestorCritique(
                    strengths=["84% gross margins are exceptional for fraud platforms because inference occurs at the edge."],
                    red_flags=["Per-transaction fees face margin compression from low-margin payment processors."],
                    hard_questions=["How will you defend pricing against commoditization from core banking features?"]
                )
            ),
            (
                7,
                SlideType.GTM,
                "Core-Banking Marketplace Co-Sell & Developer-First Led Expansion",
                "Bypassing 12-month sales cycles by distributing through pre-certified banking cores.",
                [
                    "Channel Partnerships: Pre-certified app listing in Jack Henry and Mambu app marketplaces.",
                    "Founder-led direct sales targeting top 100 fast-growth fintechs migrating to FedNow.",
                    "Open-source synthetic fraud testing tool (`sentient-mock-rail`) driving bottom-up developer discovery.",
                ],
                [
                    MetricCallout(label="Sales Cycle", value="45 Days", context="Through pre-integrated app marketplace"),
                    MetricCallout(label="CAC Payback", value="< 7 Months", context="Targeted founder-led motion"),
                    MetricCallout(label="Developer Signups", value="1,200+", context="Using open-source test kit"),
                ],
                "Instead of fighting enterprise security gatekeepers from the outside, we embed into the app store of their existing core banking vendor.",
                InvestorCritique(
                    strengths=["Marketplace distribution bypasses brutal legacy procurement roadblocks."],
                    red_flags=["Dependency on core banking platform approval and revenue share agreements."],
                    hard_questions=["What revenue share percentage do core banking marketplaces demand?"]
                )
            ),
            (
                8,
                SlideType.COMPETITION,
                "Defensibility via In-VPC Graph Execution and Zero-Egress Privacy",
                "Why legacy giants and cloud-only startups cannot replicate our speed or privacy guarantees.",
                [
                    "Legacy Players (FICO, LexisNexis): Crippled by rule engines, days-long batch updates, and high false positives.",
                    "Cloud-Only Modern Fraud (Unit21, Alloy): Require exporting PII outside bank perimeter, blocking European expansion.",
                    "Sentient Advantage: 100% In-VPC processing with sub-7ms latency and sovereign data containment.",
                ],
                [
                    MetricCallout(label="Latency Advantage", value="10x Faster", context="6.4ms vs 75ms cloud APIs"),
                    MetricCallout(label="Data Egress", value="0 Bytes", context="Full bank data sovereignty"),
                    MetricCallout(label="Model Refresh", value="Sub-Second", context="Continuous streaming graphs"),
                ],
                "Banks cannot send raw user PII to multi-tenant cloud APIs. Our zero-egress architecture wins enterprise compliance deals immediately.",
                InvestorCritique(
                    strengths=["Data sovereignty is the #1 objection in enterprise banking; solving it is a moat."],
                    red_flags=["Customer support for on-prem/VPC deployments requires specialized solutions engineering."],
                    hard_questions=["How do you deliver model updates without direct access to client infrastructure?"]
                )
            ),
            (
                9,
                SlideType.TEAM,
                "Engineered by Real-Time Systems and FinCrime Veterans",
                "Combined 24 years building mission-critical financial software at scale.",
                [
                    "Elena Rostova (CEO): Ex-Head of Fraud Engineering at Revolut; scaled payment monitoring across 35 countries.",
                    "Marcus Vance (CTO): Ex-Principal Rust Architect at Citadel; specialized in ultra-low latency transaction messaging.",
                    "Advisors: Former FinCEN Director of Intelligence and Former VP of Core Banking at Fiserv.",
                ],
                [
                    MetricCallout(label="Prior Volume", value="$40B+", context="Annual payment throughput built by founders"),
                    MetricCallout(label="Domain Experience", value="24 Years", context="High-frequency systems & FinCrime"),
                    MetricCallout(label="Patents Held", value="3 Patents", context="Distributed graph algorithms"),
                ],
                f"Our team has built and defended systems handling over $40B in payment flows. We know every vulnerability in instant settlement.",
                InvestorCritique(
                    strengths=["Elite founder-market fit combining deep fintech operational scale with high-frequency systems."],
                    red_flags=["Heavy technical leadership team; will need strong enterprise VP of Sales soon."],
                    hard_questions=["Who on the executive team has personally closed a $500k+ enterprise banking deal?"]
                )
            ),
            (
                10,
                SlideType.ASK,
                f"{ask} {round_name} Round to Accelerate Core Marketplace Rollout",
                "18 months of runway to reach $2.0M ARR and complete SOC2 Type II certification.",
                [
                    "55% Engineering & Research: Accelerate Rust in-switch agent and expand core banking connectors.",
                    "25% Enterprise Go-To-Market: Deploy dedicated banking solutions architects for marketplace pilots.",
                    "20% Compliance, Audits & Operations: Complete SOC2 Type II, ISO 27001, and regulatory certifications.",
                ],
                [
                    MetricCallout(label="Target Round", value=ask, context=f"{round_name} Round"),
                    MetricCallout(label="Runway Target", value="18 Months", context="To reach $2.0M ARR milestone"),
                    MetricCallout(label="Target ARR", value="$2.0M ARR", context="Milestone for Series A readiness"),
                ],
                f"This {ask} {round_name} round funds us through 18 months of aggressive rollout, taking us from 3 pilots to $2M ARR and Series A readiness.",
                InvestorCritique(
                    strengths=["Clear, disciplined capital allocation focused strictly on engineering and regulatory moat."],
                    red_flags=["$2M ARR in 18 months is ambitious with enterprise sales cycles; requires flawless pipeline execution."],
                    hard_questions=["What is your plan if SOC2 certification takes 6 months longer than anticipated?"]
                )
            ),
        ]

        slides = [
            Slide(
                slide_number=num,
                slide_type=st,
                headline=h,
                subtitle=sub,
                key_points=pts,
                metrics=mets,
                speaker_notes=notes,
                investor_critique=crit,
            )
            for (num, st, h, sub, pts, mets, notes, crit) in slides_data
        ]

        return PitchDeck(
            company_name=company,
            one_liner=req.one_liner or "Zero-latency autonomous compliance and fraud defense for modern fintech primitives.",
            target_round=round_name,
            target_amount=ask,
            overall_investment_thesis="Massive tailwind from instant-payment rails rendering batch fraud detection obsolete. High defensibility via low-latency in-VPC graph models.",
            overall_red_flags=[
                "Enterprise procurement cycles in tier-1 banking can span 9-14 months without design partner concessions.",
                "Potential regulatory liability if false negatives exceed contractual SLAs."
            ],
            slides=slides,
        )


deck_generator_service = DeckGeneratorService()
