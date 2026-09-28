import { CallToAction } from "@/features/landing/call-to-action";
import { Faq } from "@/features/landing/faq";
import { Hero } from "@/features/landing/hero";
import { Integrity } from "@/features/landing/integrity";
import { Preservation } from "@/features/landing/preservation";
import { Pricing } from "@/features/landing/pricing";
import { Problem } from "@/features/landing/problem";
import { Product } from "@/features/landing/product";
import { Traceability } from "@/features/landing/traceability";
import { Trust } from "@/features/landing/trust";

export default function LandingPage() {
    return (
        <>
            <Hero />
            <Problem />
            <Preservation />
            <Traceability />
            <Integrity />
            <Product />
            <Trust />
            <Pricing />
            <Faq />
            <CallToAction />
        </>
    );
}