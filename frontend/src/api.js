export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}
function validationMessage(detail) {
  if (typeof detail === "string") return detail;
  if (!Array.isArray(detail))
    return "Revisa los datos del formulario e inténtalo otra vez.";

  const labels = {
    name: "Nombre",
    email: "Email",
    password: "Contraseña",
    current_password: "Contraseña actual",
    token: "Enlace de recuperación",
  };
  const messages = detail.map((error) => {
    const field = error.loc?.[error.loc.length - 1];
    const label = labels[field];
    if (!label) return "Uno de los datos del formulario no es válido.";
    if (error.type === "missing") return label + ": completa este campo.";
    if (field === "email") return "Email: introduce una dirección válida.";
    if (field === "name")
      return "Nombre: usa entre 2 y 100 caracteres, sin contar los espacios al principio o al final.";
    if (field === "password")
      return "Contraseña: usa de 10 a 72 bytes, con al menos una mayúscula, una minúscula, un número y un símbolo. Las letras con tilde pueden ocupar más de un byte.";
    if (field === "token")
      return "El enlace de recuperación no es válido. Solicita uno nuevo.";
    return label + ": revisa el valor introducido.";
  });
  return [...new Set(messages)].join(" ") ||
    "Revisa los datos del formulario e inténtalo otra vez.";
}
export async function api(path, { token, body, signal, ...options } = {}) {
  const response = await fetch(
    (import.meta.env.VITE_API_BASE_URL || "/api") + path,
    {
      ...options,
      signal,
      headers: {
        ...(body !== undefined ? { "Content-Type": "application/json" } : {}),
        ...(token ? { Authorization: "Bearer " + token } : {}),
      },
      ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
    },
  );
  if (response.status === 204) return null;
  let data;
  try {
    data = await response.json();
  } catch {
    throw new ApiError(
      "El servidor no ha enviado una respuesta válida.",
      response.status,
    );
  }
  if (!response.ok) {
    if (response.status === 401 && token)
      window.dispatchEvent(new Event("session-expired"));
    throw new ApiError(
      validationMessage(data.detail),
      response.status,
    );
  }
  return data;
}
export const money = (value) =>
  new Intl.NumberFormat("es-ES", { style: "currency", currency: "EUR" }).format(
    Number(value),
  );
export const date = (value) =>
  new Intl.DateTimeFormat("es-ES", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
