type FormAlertProps = {
    message: string;
    requestId?: string | null;
};

/** Error general de un formulario, con el identificador de la petición si existe. */
export function FormAlert({ message, requestId }: FormAlertProps) {
    return (
        <div role="alert" className="rounded-lg border border-danger/40 bg-danger/10 px-4 py-3 text-sm">
            <p className="text-text">{message}</p>
            {requestId && (
                <p className="mt-1 text-xs text-text-subtle">
                    Referencia: <span className="font-mono select-all">{requestId}</span>
                </p>
            )}
        </div>
    );
}