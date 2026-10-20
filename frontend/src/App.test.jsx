import { beforeEach, afterEach, describe, it, expect, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import App from "./App.jsx";
const catalog = [
  {
    id: 1,
    name: "Auriculares Pro",
    description: "Sonido para cada día",
    price: "45.50",
    stock: 3,
    image_url: "https://example.com/a.jpg",
    is_active: true,
  },
  {
    id: 2,
    name: "Teclado Mini",
    description: "Un formato compacto",
    price: "20.00",
    stock: 0,
    image_url: "https://example.com/b.jpg",
    is_active: true,
  },
];
const response = (data, status = 200) =>
  Promise.resolve({
    ok: status < 400,
    status,
    json: () => Promise.resolve(data),
  });
beforeEach(() => {
  window.history.replaceState({}, "", "/");
  localStorage.clear();
  vi.stubGlobal(
    "fetch",
    vi.fn((url) =>
      response(
        String(url).endsWith("/cart") ? { items: [], total: "0" } : catalog,
      ),
    ),
  );
});
afterEach(() => vi.unstubAllGlobals());
describe("QuickShop", () => {
  it("muestra el catálogo, filtra y deshabilita productos agotados", async () => {
    const user = userEvent.setup();
    render(<App />);
    await screen.findByRole("heading", { name: "Auriculares Pro" });
    expect(
      screen.getByRole("button", { name: "Añadir Teclado Mini" }),
    ).toBeDisabled();
    await user.type(
      screen.getByRole("textbox", { name: "Buscar productos" }),
      "Auriculares",
    );
    expect(
      screen.queryByRole("heading", { name: "Teclado Mini" }),
    ).not.toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: "Auriculares Pro" }),
    ).toBeInTheDocument();
  });
  it("mantiene al usuario en acceso y muestra un error de credenciales", async () => {
    window.history.replaceState({}, "", "/acceso");
    fetch.mockImplementation(() =>
      response({ detail: "Email o contraseña incorrectos." }, 401),
    );
    const user = userEvent.setup();
    render(<App />);
    await user.type(screen.getByLabelText("Email"), "one@example.com");
    await user.type(screen.getByLabelText("Contraseña"), "Incorrecta123!");
    await user.click(
      screen.getByRole("button", { name: "Entrar en QuickShop" }),
    );
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Email o contraseña incorrectos.",
    );
    expect(window.location.pathname).toBe("/acceso");
  });
  it("inicia sesión, abre el carrito y no persiste el token en localStorage", async () => {
    window.history.replaceState({}, "", "/acceso");
    fetch.mockImplementation((url) =>
      String(url).endsWith("/auth/login")
        ? response({
            access_token: "test-token",
            user: {
              id: 1,
              name: "Cliente Uno",
              email: "one@example.com",
              role: "cliente",
            },
          })
        : response(
            String(url).endsWith("/cart") ? { items: [], total: "0" } : catalog,
          ),
    );
    const user = userEvent.setup();
    render(<App />);
    await user.type(screen.getByLabelText("Email"), "one@example.com");
    await user.type(screen.getByLabelText("Contraseña"), "Client-test123!");
    await user.click(
      screen.getByRole("button", { name: "Entrar en QuickShop" }),
    );
    await screen.findByRole("link", { name: "Cliente Uno" });
    expect(localStorage.length).toBe(0);
    await user.click(
      screen.getByRole("link", { name: "Carrito, 0 artículos" }),
    );
    expect(
      await screen.findByRole("heading", { name: /Tu carrito/ }),
    ).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Cerrar sesión" }));
    await waitFor(() =>
      expect(
        screen.getByRole("heading", { name: "Qué bueno verte de nuevo." }),
      ).toBeInTheDocument(),
    );
  });
});
