"use client";

import { useRef, useState, type ChangeEvent } from "react";

import { buttonStyles } from "@/components/ui/button-styles";
import { HashValue } from "@/components/ui/hash-value";
import { formatBytes } from "@/lib/format";
import { sha256File } from "@/lib/sha256";

/** Mismo límite que acepta la API para una evidencia. */
const MAX_BYTES = 100 * 1024 * 1024;

type SlotId = "original" | "candidate";

type SlotState =
    | { status: "empty" }
    | { status: "reading"; fileName: string }
    | { status: "ready"; fileName: string; size: number; hash: string }
    | { status: "error"; message: string };

const SLOTS: Record<SlotId, { title: string; hint: string }> = {
    original: {
        title: "Archivo preservado",
        hint: "El archivo tal como se incorporó.",
    },
    candidate: {
        title: "Archivo a verificar",
        hint: "La copia que quiere comprobar.",
    },
};

/**
 * Compara las huellas SHA-256 de dos archivos en el navegador.
 * Ningún archivo se envía a un servidor.
 */
export function IntegrityDemo() {
    const [slots, setSlots] = useState<Record<SlotId, SlotState>>({
        original: { status: "empty" },
        candidate: { status: "empty" },
    });
    const requests = useRef<Record<SlotId, number>>({ original: 0, candidate: 0 });

    function update(slot: SlotId, state: SlotState) {
        setSlots((current) => ({ ...current, [slot]: state }));
    }

    async function processFile(slot: SlotId, file: File) {
        const request = ++requests.current[slot];

        if (!window.isSecureContext) {
            update(slot, {
                status: "error",
                message: "El navegador solo permite este cálculo en conexiones seguras (HTTPS).",
            });
            return;
        }
        if (file.size > MAX_BYTES) {
            update(slot, { status: "error", message: "El archivo supera el máximo de 100 MB." });
            return;
        }

        update(slot, { status: "reading", fileName: file.name });
        try {
            const hash = await sha256File(file);
            if (request === requests.current[slot]) {
                update(slot, { status: "ready", fileName: file.name, size: file.size, hash });
            }
        } catch {
            if (request === requests.current[slot]) {
                update(slot, { status: "error", message: "No se pudo leer el archivo." });
            }
        }
    }

    const original = slots.original;
    const candidate = slots.candidate;
    const bothReady = original.status === "ready" && candidate.status === "ready";
    const matches = bothReady && original.hash === candidate.hash;

    return (
        <div className="rounded-2xl border border-border bg-card/60 p-6 sm:p-8">
            <div className="grid gap-6 md:grid-cols-2">
                <FileSlot
                    id="original"
                    state={original}
                    onFile={(file) => void processFile("original", file)}
                />
                <FileSlot
                    id="candidate"
                    state={candidate}
                    onFile={(file) => void processFile("candidate", file)}
                />
            </div>

            <div aria-live="polite" className="mt-6 border-t border-border pt-6">
                {!bothReady && (
                    <p className="text-sm leading-6 text-text-muted">
                        Seleccione los dos archivos para comparar sus huellas. El cálculo se
                        hace en este navegador; ningún archivo se envía a un servidor.
                    </p>
                )}
                {bothReady && matches && (
                    <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:gap-4">
                        <span className="inline-flex w-fit shrink-0 items-center gap-2 rounded-full border border-success/40 px-3 py-1 text-sm font-medium text-success">
                            <span aria-hidden="true" className="size-2 rounded-full bg-success" />
                            Coincide
                        </span>
                        <p className="text-sm leading-6 text-text-muted">
                            Las dos huellas son idénticas: el contenido de ambos archivos es el
                            mismo, byte a byte. El nombre del archivo no influye en la huella.
                        </p>
                    </div>
                )}
                {bothReady && !matches && (
                    <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:gap-4">
                        <span className="inline-flex w-fit shrink-0 items-center gap-2 rounded-full border border-danger/40 px-3 py-1 text-sm font-medium text-danger">
                            <span aria-hidden="true" className="size-2 rounded-full border-2 border-danger" />
                            No coincide
                        </span>
                        <p className="text-sm leading-6 text-text-muted">
                            Las huellas son distintas: el contenido no es el mismo. La huella no
                            indica qué cambió ni cuánto, solo que hay una diferencia.
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
}

type FileSlotProps = {
    id: SlotId;
    state: SlotState;
    onFile: (file: File) => void;
};

function FileSlot({ id, state, onFile }: FileSlotProps) {
    const inputRef = useRef<HTMLInputElement>(null);
    const { title, hint } = SLOTS[id];

    function handleChange(event: ChangeEvent<HTMLInputElement>) {
        const file = event.target.files?.[0];
        event.target.value = "";
        if (file) {
            onFile(file);
        }
    }

    return (
        <div className="flex min-h-56 flex-col rounded-xl border border-border bg-elevated p-5">
            <h3 className="font-medium">{title}</h3>
            <p className="mt-1 text-sm text-text-muted">{hint}</p>

            <input
                ref={inputRef}
                type="file"
                onChange={handleChange}
                className="sr-only"
                tabIndex={-1}
                aria-hidden="true"
            />

            <div className="mt-5 flex-1">
                {state.status === "empty" && (
                    <p className="text-sm text-text-subtle">Ningún archivo seleccionado.</p>
                )}
                {state.status === "reading" && (
                    <p className="text-sm text-text-muted">Calculando la huella de {state.fileName}…</p>
                )}
                {state.status === "error" && <p className="text-sm text-danger">{state.message}</p>}
                {state.status === "ready" && (
                    <>
                        <p className="text-sm">
                            <span className="font-medium break-all">{state.fileName}</span>
                            <span className="text-text-muted"> ({formatBytes(state.size)})</span>
                        </p>
                        <HashValue value={state.hash} className="mt-3 text-text-muted" />
                    </>
                )}
            </div>

            <button
                type="button"
                onClick={() => inputRef.current?.click()}
                className={`${buttonStyles("secondary")} mt-5 self-start`}
            >
                {state.status === "ready" ? "Cambiar archivo" : "Seleccionar archivo"}
            </button>
        </div>
    );
}