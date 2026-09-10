"use client";

import { useEffect } from "react";

export function ExtensionAttributeCleaner() {
  useEffect(() => {
    // Clean up extension-injected attributes that cause React dev overlay warnings
    const removeExtensionAttributes = () => {
      document.querySelectorAll("[bis_skin_checked]").forEach((el) => {
        el.removeAttribute("bis_skin_checked");
      });
      document.querySelectorAll("[bis_register]").forEach((el) => {
        el.removeAttribute("bis_register");
      });
      if (document.body) {
        document.body.removeAttribute("bis_register");
        Array.from(document.body.attributes).forEach((attr) => {
          if (attr.name.startsWith("__processed_")) {
            document.body.removeAttribute(attr.name);
          }
        });
      }
    };

    removeExtensionAttributes();

    const observer = new MutationObserver((mutations) => {
      for (const mutation of mutations) {
        if (
          mutation.type === "attributes" &&
          (mutation.attributeName === "bis_skin_checked" ||
            mutation.attributeName === "bis_register" ||
            mutation.attributeName?.startsWith("__processed_"))
        ) {
          (mutation.target as HTMLElement).removeAttribute(mutation.attributeName);
        }
      }
    });

    observer.observe(document.documentElement, {
      attributes: true,
      subtree: true,
      attributeFilter: ["bis_skin_checked", "bis_register"],
    });

    return () => observer.disconnect();
  }, []);

  return null;
}
