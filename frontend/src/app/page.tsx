"use client";

import dynamic from "next/dynamic";

const PitchBuilderApp = dynamic(
  () => import("@/components/PitchBuilderApp"),
  { ssr: false }
);

export default function Page() {
  return <PitchBuilderApp />;
}
