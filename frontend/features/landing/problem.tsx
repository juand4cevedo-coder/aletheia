const POINTS = [
    {
        title: "Una copia no explica su origen",
        body: "Una carpeta en la nube conserva el archivo, pero no deja un registro verificable de quién lo incorporó, cuándo ni para qué caso.",
    },
    {
        title: "La integridad necesita una referencia",
        body: "Para mostrar que un archivo no cambió hace falta una huella registrada en el momento de preservarlo, no calculada después.",
    },
    {
        title: "El contexto se dispersa",
        body: "Correos, chats, memorias USB y descargas separan la evidencia del asunto al que pertenece. El caso es lo que le da contexto.",
    },
] as const;

export function Problem() {
    return (
        <section aria-labelledby="problema" className="mx-auto w-full max-w-6xl px-6 py-24">
            <div className="grid gap-12 rounded-3xl border border-border bg-elevated p-8 sm:p-12 lg:grid-cols-[1fr_1.1fr] lg:gap-16">
                <div>
                    <p className="text-xs font-medium tracking-[0.18em] text-accent uppercase">
                        El problema
                    </p>
                    <h2
                        id="problema"
                        className="mt-4 text-4xl leading-[1.05] font-semibold tracking-tight text-balance sm:text-5xl"
                    >
                        Guardar un archivo no es lo mismo que preservarlo.
                    </h2>
                    <p className="mt-6 max-w-md text-lg leading-8 text-text-muted">
                        La evidencia digital necesita algo más que almacenamiento: contexto,
                        trazabilidad y una forma de comprobar qué ocurrió con ella.
                    </p>
                </div>

                <ul className="divide-y divide-border self-center border-y border-border">
                    {POINTS.map((point) => (
                        <li key={point.title} className="py-6">
                            <h3 className="text-lg font-medium">{point.title}</h3>
                            <p className="mt-2 leading-7 text-text-muted">{point.body}</p>
                        </li>
                    ))}
                </ul>
            </div>
        </section>
    );
}