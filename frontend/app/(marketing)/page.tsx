import { Hero } from "@/features/landing/hero";
import { Integrity } from "@/features/landing/integrity";
import { Preservation } from "@/features/landing/preservation";
import { Problem } from "@/features/landing/problem";
import { Traceability } from "@/features/landing/traceability";

export default function LandingPage() {
    return (
        <>
            <Hero />
            <Problem />
            <Preservation />
            <Traceability />
            <Integrity />
        </>
    );
}