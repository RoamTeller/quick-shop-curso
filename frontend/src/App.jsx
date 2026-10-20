import { createContext, useContext, useState, useEffect, useRef } from "react";
import {
  BrowserRouter,
  Routes,
  Route,
  Link,
  NavLink,
  Navigate,
  useNavigate,
  useLocation,
  useParams,
} from "react-router-dom";
import { api, money, date } from "./api.js";
import { Icon } from "./icons.jsx";
const Auth = createContext(null);
const Notice = createContext(() => {});
function useAuth() {
  return useContext(Auth);
}
function useAction() {
  const [busy, setBusy] = useState(false),
    [error, setError] = useState("");
  const active = useRef(false);
  async function run(action) {
    if (active.current) return;
    active.current = true;
    setBusy(true);
    setError("");
    try {
      return await action();
    } catch (e) {
      setError(e.message || "No se pudo completar la operación.");
    } finally {
      active.current = false;
      setBusy(false);
    }
  }
  return { busy, error, run };
}
function useResource(path, initial = null, enabled = true) {
  const { token } = useAuth();
  const [data, setData] = useState(initial),
    [loading, setLoading] = useState(enabled),
    [error, setError] = useState(""),
    [version, setVersion] = useState(0);
  useEffect(() => {
    if (!enabled) {
      setData(initial);
      setLoading(false);
      return;
    }
    const controller = new AbortController();
    setLoading(true);
    setError("");
    api(path, { token, signal: controller.signal })
      .then(setData)
      .catch((e) => {
        if (e.name !== "AbortError") setError(e.message);
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [path, token, version, enabled]);
  return { data, loading, error, refresh: () => setVersion((v) => v + 1) };
}
function ErrorBox({ message }) {
  return message ? (
    <p className="alert error" role="alert">
      {message}
    </p>
  ) : null;
}
function ResourceState({ resource, children }) {
  if (resource.loading)
    return (
      <div className="loading" role="status">
        <span className="spinner" />
        Cargando…
      </div>
    );
  if (resource.error)
    return (
      <div className="state">
        <ErrorBox message={resource.error} />
        <button className="button secondary" onClick={resource.refresh}>
          Volver a intentar
        </button>
      </div>
    );
  return children;
}
function Guard({ admin = false, children }) {
  const { user } = useAuth(),
    location = useLocation();
  if (!user)
    return (
      <Navigate to="/acceso" replace state={{ from: location.pathname }} />
    );
  if (admin && user.role !== "administrador")
    return <Navigate to="/" replace />;
  return children;
}
function Image({ product }) {
  const [failed, setFailed] = useState(false);
  return failed ? (
    <div className="image-placeholder">
      <Icon name="box" size={42} />
      <span>{product.name}</span>
    </div>
  ) : (
    <img
      src={product.image_url}
      alt={product.name}
      loading="lazy"
      onError={() => setFailed(true)}
    />
  );
}
function Header() {
  const { user, logout } = useAuth();
  const cart = useResource("/cart", { items: [] }, user?.role === "cliente");
  useEffect(() => {
    const handler = () => cart.refresh();
    window.addEventListener("cart-updated", handler);
    return () => window.removeEventListener("cart-updated", handler);
  }, []);
  const count = cart.data?.items?.reduce((n, i) => n + i.quantity, 0) || 0;
  return (
    <>
      <div className="top-note">
        Lo esencial, bien elegido.
        <span>Tu próxima buena compra empieza aquí.</span>
      </div>
      <header className="header">
        <Link className="logo" to="/">
          <span className="logo-icon">
            <Icon name="bag" size={22} />
          </span>
          QuickShop<span className="logo-dot">.</span>
        </Link>
        <nav aria-label="Navegación principal">
          <NavLink to="/" end>
            Catálogo
          </NavLink>
          {user && (
            <NavLink to="/pedidos">
              {user.role === "administrador" ? "Pedidos" : "Mis pedidos"}
            </NavLink>
          )}
          {user?.role === "administrador" && (
            <NavLink to="/admin">Productos</NavLink>
          )}
        </nav>
        <div className="header-actions">
          {user ? (
            <>
              <Link className="account-link" to="/perfil">
                <Icon name="user" size={18} />
                <span>{user.name}</span>
              </Link>
              <button
                className="icon-button logout"
                aria-label="Cerrar sesión"
                onClick={logout}
              >
                <Icon name="exit" size={19} />
              </button>
            </>
          ) : (
            <Link className="account-link" to="/acceso">
              <Icon name="user" size={18} />
              <span>Mi cuenta</span>
            </Link>
          )}
          {user?.role !== "administrador" && (
            <Link
              className="cart-link"
              to="/carrito"
              aria-label={"Carrito, " + count + " artículos"}
            >
              <Icon name="bag" size={21} />
              <span>{count}</span>
            </Link>
          )}
        </div>
      </header>
    </>
  );
}
function Catalog() {
  const resource = useResource("/products", []),
    [search, setSearch] = useState(""),
    [sort, setSort] = useState("default");
  const { user, token } = useAuth(),
    notify = useContext(Notice),
    navigate = useNavigate(),
    action = useAction();
  let products = (resource.data || []).filter((p) =>
    (p.name + " " + p.description).toLowerCase().includes(search.toLowerCase()),
  );
  if (sort !== "default")
    products = [...products].sort((a, b) =>
      sort === "price-up"
        ? Number(a.price) - Number(b.price)
        : sort === "price-down"
          ? Number(b.price) - Number(a.price)
          : a.name.localeCompare(b.name),
    );
  async function add(product) {
    if (!user) {
      navigate("/acceso");
      return;
    }
    await action.run(async () => {
      await api("/cart/items", {
        method: "POST",
        token,
        body: { product_id: product.id, quantity: 1 },
      });
      window.dispatchEvent(new Event("cart-updated"));
      notify("Añadido al carrito: " + product.name);
    });
  }
  return (
    <>
      <section className="hero">
        <div className="hero-copy">
          <span className="eyebrow">
            <span />
            LA SELECCIÓN QUICKSHOP
          </span>
          <h1>
            Pequeños cambios.
            <br />
            Grandes días<span>.</span>
          </h1>
          <p>
            Tecnología y accesorios que encajan contigo.
            <br className="desktop-break" /> Descubre lo que le faltaba a tu día
            a día.
          </p>
          <a className="button primary" href="#catalogo">
            Explorar la colección
            <Icon name="arrow" size={18} />
          </a>
          <div className="hero-caption">
            <span>01 /</span> Una selección para cada día.
          </div>
        </div>
        <div className="hero-art" aria-hidden="true">
          <div className="art-grid" />
          <div className="art-circle" />
          <div className="art-headphones">
            <div className="headband" />
            <div className="ear left" />
            <div className="ear right" />
          </div>
          <div className="art-card">
            <span>
              EVERYDAY
              <br />
              ESSENTIALS
            </span>
            <Icon name="arrow" size={32} />
          </div>
          <span className="vertical-note">DISEÑADO PARA TU RUTINA</span>
          <div className="floating-label">
            Encuentra tu próximo favorito
            <Icon name="plus" size={15} />
          </div>
        </div>
      </section>
      <div className="benefits">
        <span>
          <Icon name="box" size={18} />
          Una selección con propósito
        </span>
        <span>
          <Icon name="shield" size={18} />
          Tu cuenta, bajo tu control
        </span>
        <span>
          <Icon name="check" size={18} />
          Tus pedidos en un solo lugar
        </span>
      </div>
      <section id="catalogo" className="catalog-section">
        <div className="section-heading">
          <div>
            <p className="eyebrow">ENCUENTRA LO TUYO</p>
            <h2>
              La colección<span> / {resource.data?.length || 0}</span>
            </h2>
          </div>
          <p>Todo lo que necesitas. Nada de más.</p>
        </div>
        <div className="catalog-toolbar">
          <label className="search-box">
            <Icon name="search" size={18} />
            <span className="sr-only">Buscar productos</span>
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Busca tu próximo favorito…"
            />
          </label>
          <label className="sort-box">
            Ordenar por
            <select
              aria-label="Ordenar productos"
              value={sort}
              onChange={(e) => setSort(e.target.value)}
            >
              <option value="default">Recomendados</option>
              <option value="price-up">Menor precio</option>
              <option value="price-down">Mayor precio</option>
              <option value="name">Nombre</option>
            </select>
          </label>
        </div>
        <ErrorBox message={action.error} />
        <ResourceState resource={resource}>
          {!products.length ? (
            <div className="empty">
              <Icon name="search" size={36} />
              <h3>No encontramos esos productos.</h3>
              <p>Prueba con otro nombre o cambia tu búsqueda.</p>
              <button className="text-button" onClick={() => setSearch("")}>
                Ver toda la colección
              </button>
            </div>
          ) : (
            <div className="product-grid">
              {products.map((p, i) => (
                <article className="product-card" key={p.id}>
                  <Link to={"/productos/" + p.id} className="product-image">
                    <Image product={p} />
                    {p.stock === 0 ? (
                      <span className="stock-label out">Agotado</span>
                    ) : (
                      i < 3 &&
                      !search && (
                        <span className="stock-label">La selección</span>
                      )
                    )}
                    <span className="image-arrow">
                      <Icon name="arrow" size={17} />
                    </span>
                  </Link>
                  <div className="product-details">
                    <span className="product-category">
                      QUICKSHOP ESSENTIALS
                    </span>
                    <Link to={"/productos/" + p.id}>
                      <h3>{p.name}</h3>
                    </Link>
                    <p>{p.description}</p>
                    <div className="product-bottom">
                      <strong>{money(p.price)}</strong>
                      {user?.role !== "administrador" && (
                        <button
                          className="add-button"
                          disabled={p.stock === 0 || action.busy}
                          aria-label={"Añadir " + p.name}
                          onClick={() => add(p)}
                        >
                          <Icon name="plus" size={19} />
                        </button>
                      )}
                    </div>
                  </div>
                </article>
              ))}
            </div>
          )}
        </ResourceState>
      </section>
      <section className="closing-banner">
        <div>
          <span className="eyebrow">MENOS RUIDO. MÁS ESENCIALES.</span>
          <h2>
            Tu día a día,
            <br />
            un poco mejor.
          </h2>
        </div>
        <span className="closing-word" aria-hidden="true">
          Q.
        </span>
        <Link className="button secondary" to={user ? "/perfil" : "/registro"}>
          {user ? "Tu espacio QuickShop" : "Crea tu cuenta"}
          <Icon name="arrow" size={17} />
        </Link>
      </section>
    </>
  );
}
function ProductDetail() {
  const { id } = useParams(),
    resource = useResource("/products/" + id),
    { user, token } = useAuth(),
    action = useAction(),
    notify = useContext(Notice),
    navigate = useNavigate();
  return (
    <div className="page">
      <Link className="back-link" to="/">
        Volver al catálogo
      </Link>
      <ResourceState resource={resource}>
        {resource.data && (
          <div className="product-detail">
            <div className="detail-image">
              <Image product={resource.data} />
            </div>
            <div>
              <span className="eyebrow">QUICKSHOP ESSENTIALS</span>
              <h1>{resource.data.name}</h1>
              <p>{resource.data.description}</p>
              <strong className="detail-price">
                {money(resource.data.price)}
              </strong>
              <p className="muted">
                {resource.data.stock > 0
                  ? resource.data.stock + " unidades disponibles"
                  : "Producto agotado"}
              </p>
              <ErrorBox message={action.error} />
              {user?.role !== "administrador" && (
                <button
                  className="button primary"
                  disabled={action.busy || resource.data.stock === 0}
                  onClick={() => {
                    if (!user) {
                      navigate("/acceso", {
                        state: { from: "/productos/" + id },
                      });
                      return;
                    }
                    action.run(async () => {
                      await api("/cart/items", {
                        method: "POST",
                        token,
                        body: { product_id: Number(id), quantity: 1 },
                      });
                      window.dispatchEvent(new Event("cart-updated"));
                      notify("Producto añadido al carrito");
                    });
                  }}
                >
                  Añadir al carrito
                  <Icon name="bag" size={17} />
                </button>
              )}
            </div>
          </div>
        )}
      </ResourceState>
    </div>
  );
}
function AuthPage({ kind }) {
  const navigate = useNavigate(),
    location = useLocation(),
    { login } = useAuth(),
    notify = useContext(Notice),
    action = useAction();
  const [values, setValues] = useState({ name: "", email: "", password: "" }),
    [success, setSuccess] = useState("");
  const register = kind === "register",
    forgot = kind === "forgot",
    reset = kind === "reset";
  const title = register
    ? "Tu espacio empieza aquí."
    : forgot
      ? "Recupera tu acceso."
      : reset
        ? "Un nuevo comienzo."
        : "Qué bueno verte de nuevo.";
  async function submit(e) {
    e.preventDefault();
    await action.run(async () => {
      if (forgot) {
        const data = await api("/auth/forgot-password", {
          method: "POST",
          body: { email: values.email },
        });
        setSuccess(data.message);
        return;
      }
      if (reset) {
        const token =
          new URLSearchParams(location.hash.slice(1)).get("token") || "";
        const data = await api("/auth/reset-password", {
          method: "POST",
          body: { token, password: values.password },
        });
        notify(data.message);
        navigate("/acceso");
        return;
      }
      if (register)
        await api("/auth/register", { method: "POST", body: values });
      const data = await api("/auth/login", {
        method: "POST",
        body: { email: values.email, password: values.password },
      });
      login(data);
      navigate(location.state?.from || "/");
      notify(register ? "Tu cuenta ya está lista." : "Has iniciado sesión.");
    });
  }
  return (
    <section className="auth-layout">
      <div className="auth-story">
        <span className="eyebrow">BIENVENIDO A QUICKSHOP</span>
        <h1>
          Lo esencial
          <br />
          empieza
          <br />
          contigo<span>.</span>
        </h1>
        <div className="story-art" aria-hidden="true">
          <Icon name="bag" size={110} />
        </div>
        <p>
          Encuentra tus favoritos.
          <br />
          Hazlos parte de tu día.
        </p>
      </div>
      <div className="auth-form-wrap">
        <Link to="/" className="back-link">
          Volver a la tienda
        </Link>
        <span className="eyebrow">
          {register
            ? "CREAR CUENTA"
            : forgot || reset
              ? "TU CUENTA"
              : "INICIAR SESIÓN"}
        </span>
        <h2>{title}</h2>
        <p className="muted">
          {register
            ? "Guarda tus productos en el carrito y consulta tus pedidos."
            : forgot
              ? "Te enviaremos un enlace para cambiar tu contraseña."
              : reset
                ? "Elige una contraseña nueva para proteger tu cuenta."
                : "Entra en tu cuenta y sigue donde lo dejaste."}
        </p>
        {success ? (
          <div className="alert success" role="status">
            {success}
          </div>
        ) : (
          <form onSubmit={submit}>
            {register && (
              <label>
                Nombre
                <input
                  autoComplete="name"
                  required
                  minLength={2}
                  maxLength={100}
                  value={values.name}
                  onChange={(e) =>
                    setValues({ ...values, name: e.target.value })
                  }
                />
              </label>
            )}
            {!reset && (
              <label>
                Email
                <input
                  type="email"
                  autoComplete="email"
                  required
                  value={values.email}
                  onChange={(e) =>
                    setValues({ ...values, email: e.target.value })
                  }
                />
              </label>
            )}
            {!forgot && (
              <label>
                {reset ? "Nueva contraseña" : "Contraseña"}
                <input
                  type="password"
                  autoComplete={
                    register || reset ? "new-password" : "current-password"
                  }
                  required
                  minLength={register || reset ? 10 : 1}
                  maxLength={72}
                  value={values.password}
                  onChange={(e) =>
                    setValues({ ...values, password: e.target.value })
                  }
                />
              </label>
            )}
            {(register || reset) && (
              <p className="field-note">
                De 10 a 72 bytes: mayúscula, minúscula, número y símbolo.
              </p>
            )}
            <ErrorBox message={action.error} />
            <button className="button primary full" disabled={action.busy}>
              {action.busy
                ? "Un momento…"
                : register
                  ? "Crear mi cuenta"
                  : forgot
                    ? "Enviar enlace"
                    : reset
                      ? "Actualizar contraseña"
                      : "Entrar en QuickShop"}
              <Icon name="arrow" size={17} />
            </button>
          </form>
        )}
        {!forgot && !reset && (
          <>
            <p className="auth-link">
              {register ? "¿Ya tienes cuenta?" : "¿Es tu primera visita?"}{" "}
              <Link to={register ? "/acceso" : "/registro"}>
                {register ? "Inicia sesión" : "Crea tu cuenta"}
              </Link>
            </p>
            {!register && (
              <Link className="forgot-link" to="/recuperar">
                ¿Has olvidado tu contraseña?
              </Link>
            )}
          </>
        )}
        {(forgot || reset) && (
          <Link className="forgot-link" to="/acceso">
            Volver a iniciar sesión
          </Link>
        )}
      </div>
    </section>
  );
}
function CartPage() {
  const resource = useResource("/cart", { items: [], total: "0" }),
    { token, user } = useAuth(),
    action = useAction(),
    notify = useContext(Notice),
    navigate = useNavigate();
  async function change(path, options) {
    await action.run(async () => {
      await api(path, { token, ...options });
      resource.refresh();
      window.dispatchEvent(new Event("cart-updated"));
    });
  }
  if (user?.role === "administrador") return <Navigate to="/admin" replace />;
  return (
    <div className="page">
      <p className="eyebrow">TUS PRÓXIMOS FAVORITOS</p>
      <h1>
        Tu carrito<span>.</span>
      </h1>
      <ResourceState resource={resource}>
        <ErrorBox message={action.error} />
        {!resource.data.items.length ? (
          <div className="empty">
            <Icon name="bag" size={45} />
            <h2>Un espacio para lo que te gusta.</h2>
            <p>Explora la colección y añade tu primer favorito.</p>
            <Link className="button primary" to="/">
              Descubrir productos
              <Icon name="arrow" size={17} />
            </Link>
          </div>
        ) : (
          <div className="cart-layout">
            <div>
              {resource.data.items.map((item) => (
                <article className="cart-row" key={item.product.id}>
                  <Link
                    to={"/productos/" + item.product.id}
                    className="cart-thumb"
                  >
                    <Image product={item.product} />
                  </Link>
                  <div className="cart-info">
                    <Link to={"/productos/" + item.product.id}>
                      <h3>{item.product.name}</h3>
                    </Link>
                    <p>{money(item.product.price)} / unidad</p>
                    <button
                      className="text-button muted"
                      disabled={action.busy}
                      onClick={() =>
                        change("/cart/items/" + item.product.id, {
                          method: "DELETE",
                        })
                      }
                    >
                      Eliminar
                    </button>
                  </div>
                  <div className="quantity-control">
                    <button
                      aria-label={"Reducir " + item.product.name}
                      disabled={action.busy || item.quantity <= 1}
                      onClick={() =>
                        change("/cart/items/" + item.product.id, {
                          method: "PATCH",
                          body: { quantity: item.quantity - 1 },
                        })
                      }
                    >
                      <Icon name="minus" size={14} />
                    </button>
                    <span>{item.quantity}</span>
                    <button
                      aria-label={"Aumentar " + item.product.name}
                      disabled={
                        action.busy || item.quantity >= item.product.stock
                      }
                      onClick={() =>
                        change("/cart/items/" + item.product.id, {
                          method: "PATCH",
                          body: { quantity: item.quantity + 1 },
                        })
                      }
                    >
                      <Icon name="plus" size={14} />
                    </button>
                  </div>
                  <strong>{money(item.subtotal)}</strong>
                </article>
              ))}
              <button
                className="text-button"
                disabled={action.busy}
                onClick={() => change("/cart", { method: "DELETE" })}
              >
                Vaciar carrito
              </button>
            </div>
            <aside className="summary">
              <span className="eyebrow">CASI ES TUYO</span>
              <h2>Resumen del pedido</h2>
              <div>
                <span>Productos</span>
                <span>
                  {resource.data.items.reduce((n, i) => n + i.quantity, 0)}
                </span>
              </div>
              <div className="summary-total">
                <span>Total</span>
                <strong>{money(resource.data.total)}</strong>
              </div>
              <p>
                El stock y los precios se comprueban de nuevo al crear el
                pedido.
              </p>
              <button
                className="button primary full"
                disabled={action.busy}
                onClick={() =>
                  action.run(async () => {
                    const order = await api("/orders", {
                      method: "POST",
                      token,
                    });
                    window.dispatchEvent(new Event("cart-updated"));
                    notify("Pedido creado correctamente.");
                    navigate("/pedidos/" + order.id);
                  })
                }
              >
                {action.busy ? "Creando pedido…" : "Crear pedido"}
                <Icon name="arrow" size={17} />
              </button>
              <span className="field-note">
                Demo del curso: no se realiza ningún cobro.
              </span>
            </aside>
          </div>
        )}
      </ResourceState>
    </div>
  );
}
function OrdersPage() {
  const resource = useResource("/orders", []),
    { user } = useAuth();
  return (
    <div className="page">
      <p className="eyebrow">CADA PEDIDO, EN SU SITIO</p>
      <h1>
        {user.role === "administrador" ? "Todos los pedidos" : "Mis pedidos"}
        <span>.</span>
      </h1>
      <ResourceState resource={resource}>
        {!resource.data.length ? (
          <div className="empty">
            <Icon name="box" size={42} />
            <h2>Aún no hay pedidos.</h2>
            <Link className="button primary" to="/">
              Volver al catálogo
            </Link>
          </div>
        ) : (
          <div className="order-list">
            {resource.data.map((order) => (
              <Link
                className="order-row"
                to={"/pedidos/" + order.id}
                key={order.id}
              >
                <div className="order-icon">
                  <Icon name="box" size={24} />
                </div>
                <div>
                  <h3>Pedido #{order.id.toString().padStart(4, "0")}</h3>
                  <p>
                    {date(order.created_at)} ·{" "}
                    {order.items.reduce((n, i) => n + i.quantity, 0)} artículos
                    {user.role === "administrador"
                      ? " · Cliente #" + order.user_id
                      : ""}
                  </p>
                </div>
                <span className={"status " + order.status}>{order.status}</span>
                <strong>{money(order.total)}</strong>
                <Icon name="arrow" size={17} />
              </Link>
            ))}
          </div>
        )}
      </ResourceState>
    </div>
  );
}
function OrderDetail() {
  const { id } = useParams(),
    resource = useResource("/orders/" + id),
    { user, token } = useAuth(),
    action = useAction(),
    notify = useContext(Notice);
  const transitions = {
    pendiente: ["confirmado", "cancelado"],
    confirmado: ["enviado", "cancelado"],
    enviado: ["entregado", "cancelado"],
  };
  return (
    <div className="page">
      <Link className="back-link" to="/pedidos">
        Volver a pedidos
      </Link>
      <ResourceState resource={resource}>
        {resource.data && (
          <>
            <div className="section-heading">
              <div>
                <p className="eyebrow">{date(resource.data.created_at)}</p>
                <h1>Pedido #{id.padStart(4, "0")}</h1>
              </div>
              <span className={"status " + resource.data.status}>
                {resource.data.status}
              </span>
            </div>
            <div className="order-lines">
              {resource.data.items.map((item) => (
                <div key={item.product_id}>
                  <div>
                    <h3>{item.product_name}</h3>
                    <span>
                      {item.quantity} × {money(item.unit_price)}
                    </span>
                  </div>
                  <strong>
                    {money(Number(item.unit_price) * item.quantity)}
                  </strong>
                </div>
              ))}
            </div>
            <div className="order-total">
              Total del pedido<strong>{money(resource.data.total)}</strong>
            </div>
            <ErrorBox message={action.error} />
            <div className="order-actions">
              {user.role === "administrador" &&
                (transitions[resource.data.status] || []).map((status) => (
                  <button
                    key={status}
                    className={
                      "button " +
                      (status === "cancelado" ? "secondary" : "primary")
                    }
                    disabled={action.busy}
                    onClick={() =>
                      action.run(async () => {
                        await api("/admin/orders/" + id + "/status", {
                          method: "PATCH",
                          token,
                          body: { status },
                        });
                        resource.refresh();
                        notify("Estado actualizado.");
                      })
                    }
                  >
                    {status === "cancelado"
                      ? "Cancelar pedido"
                      : "Marcar como " + status}
                  </button>
                ))}
              {user.role === "cliente" &&
                resource.data.status === "pendiente" && (
                  <button
                    className="button secondary"
                    disabled={action.busy}
                    onClick={() =>
                      action.run(async () => {
                        await api("/orders/" + id + "/cancel", {
                          method: "POST",
                          token,
                        });
                        resource.refresh();
                        notify("Pedido cancelado.");
                      })
                    }
                  >
                    Cancelar pedido
                  </button>
                )}
            </div>
          </>
        )}
      </ResourceState>
    </div>
  );
}
function Profile() {
  const { user, token, logout } = useAuth(),
    action = useAction(),
    notify = useContext(Notice),
    navigate = useNavigate();
  const [values, setValues] = useState({ current_password: "", password: "" });
  return (
    <div className="page profile-page">
      <span className="eyebrow">TU ESPACIO QUICKSHOP</span>
      <h1>
        Hola, {user.name}
        <span>.</span>
      </h1>
      <div className="profile-data">
        <Icon name="user" size={28} />
        <div>
          <strong>{user.email}</strong>
          <p>
            {user.role === "administrador"
              ? "Cuenta de administrador"
              : "Cuenta de cliente"}
          </p>
        </div>
      </div>
      <form
        className="panel password-form"
        onSubmit={(e) => {
          e.preventDefault();
          action.run(async () => {
            const data = await api("/auth/change-password", {
              method: "POST",
              token,
              body: values,
            });
            logout();
            notify(data.message);
            navigate("/acceso");
          });
        }}
      >
        <h2>Cambiar contraseña</h2>
        <p className="muted">Al actualizarla se cerrarán todas tus sesiones.</p>
        <label>
          Contraseña actual
          <input
            type="password"
            autoComplete="current-password"
            required
            value={values.current_password}
            onChange={(e) =>
              setValues({ ...values, current_password: e.target.value })
            }
          />
        </label>
        <label>
          Nueva contraseña
          <input
            type="password"
            autoComplete="new-password"
            required
            minLength={10}
            maxLength={72}
            value={values.password}
            onChange={(e) => setValues({ ...values, password: e.target.value })}
          />
        </label>
        <p className="field-note">
          De 10 a 72 bytes: mayúscula, minúscula, número y símbolo.
        </p>
        <ErrorBox message={action.error} />
        <button className="button primary" disabled={action.busy}>
          {action.busy ? "Guardando…" : "Actualizar contraseña"}
        </button>
      </form>
    </div>
  );
}
const emptyProduct = {
  name: "",
  description: "",
  price: "",
  stock: 0,
  image_url: "",
  is_active: true,
};
function ProductForm({ product, onClose, onSaved }) {
  const [data, setData] = useState(product || emptyProduct),
    { token } = useAuth(),
    action = useAction(),
    dialog = useRef();
  useEffect(() => {
    dialog.current.showModal();
    return () => dialog.current?.close();
  }, []);
  return (
    <dialog ref={dialog} className="product-modal" onCancel={onClose}>
      <button
        className="modal-close icon-button"
        aria-label="Cerrar formulario"
        onClick={onClose}
      >
        <Icon name="close" />
      </button>
      <p className="eyebrow">ADMINISTRACIÓN</p>
      <h2>{product ? "Editar producto" : "Un nuevo esencial"}</h2>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          action.run(async () => {
            await api("/admin/products" + (product ? "/" + product.id : ""), {
              method: product ? "PUT" : "POST",
              token,
              body: {
                name: data.name,
                description: data.description,
                price: String(data.price),
                stock: Number(data.stock),
                image_url: data.image_url,
                is_active: data.is_active,
              },
            });
            onSaved();
            onClose();
          });
        }}
      >
        <label>
          Nombre
          <input
            required
            minLength={2}
            maxLength={150}
            value={data.name}
            onChange={(e) => setData({ ...data, name: e.target.value })}
          />
        </label>
        <label>
          Descripción
          <textarea
            required
            minLength={3}
            maxLength={2000}
            value={data.description}
            onChange={(e) => setData({ ...data, description: e.target.value })}
          />
        </label>
        <div className="form-grid">
          <label>
            Precio (€)
            <input
              type="number"
              min="0.01"
              step="0.01"
              max="99999999.99"
              required
              value={data.price}
              onChange={(e) => setData({ ...data, price: e.target.value })}
            />
          </label>
          <label>
            Stock
            <input
              type="number"
              min="0"
              max="1000000"
              step="1"
              required
              value={data.stock}
              onChange={(e) => setData({ ...data, stock: e.target.value })}
            />
          </label>
        </div>
        <label>
          URL de imagen
          <input
            type="url"
            required
            maxLength={2000}
            value={data.image_url}
            onChange={(e) => setData({ ...data, image_url: e.target.value })}
          />
        </label>
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={data.is_active}
            onChange={(e) => setData({ ...data, is_active: e.target.checked })}
          />
          Producto activo
        </label>
        <ErrorBox message={action.error} />
        <button className="button primary full" disabled={action.busy}>
          {action.busy ? "Guardando…" : "Guardar producto"}
        </button>
      </form>
    </dialog>
  );
}
function Admin() {
  const resource = useResource("/admin/products", []),
    { token } = useAuth(),
    action = useAction(),
    notify = useContext(Notice),
    [form, setForm] = useState(undefined);
  return (
    <div className="page">
      <div className="section-heading">
        <div>
          <p className="eyebrow">ADMINISTRACIÓN</p>
          <h1>
            Tu catálogo<span>.</span>
          </h1>
        </div>
        <button className="button primary" onClick={() => setForm(null)}>
          <Icon name="plus" size={17} />
          Nuevo producto
        </button>
      </div>
      <ErrorBox message={action.error} />
      <ResourceState resource={resource}>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Producto</th>
                <th>Precio</th>
                <th>Stock</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {resource.data.map((p) => (
                <tr key={p.id}>
                  <td>
                    <div className="admin-product">
                      <div className="table-image">
                        <Image product={p} />
                      </div>
                      <span>{p.name}</span>
                    </div>
                  </td>
                  <td>{money(p.price)}</td>
                  <td>{p.stock}</td>
                  <td>
                    <span
                      className={
                        "status " + (p.is_active ? "activo" : "cancelado")
                      }
                    >
                      {p.is_active ? "Activo" : "Inactivo"}
                    </span>
                  </td>
                  <td>
                    <div className="table-actions">
                      <button
                        className="text-button"
                        onClick={() => setForm(p)}
                      >
                        Editar
                      </button>
                      {p.is_active && (
                        <button
                          className="text-button muted"
                          disabled={action.busy}
                          onClick={() =>
                            action.run(async () => {
                              await api("/admin/products/" + p.id, {
                                method: "DELETE",
                                token,
                              });
                              resource.refresh();
                              notify("Producto desactivado.");
                            })
                          }
                        >
                          Desactivar
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </ResourceState>
      {form !== undefined && (
        <ProductForm
          product={form}
          onClose={() => setForm(undefined)}
          onSaved={() => {
            resource.refresh();
            notify("Producto guardado.");
          }}
        />
      )}
    </div>
  );
}
function Shell() {
  const [user, setUser] = useState(null),
    [token, setToken] = useState(""),
    [notice, setNotice] = useState("");
  function logout() {
    setToken("");
    setUser(null);
    window.dispatchEvent(new Event("cart-updated"));
  }
  useEffect(() => {
    const handler = () => {
      logout();
      setNotice("Tu sesión ha caducado. Inicia sesión de nuevo.");
    };
    window.addEventListener("session-expired", handler);
    return () => window.removeEventListener("session-expired", handler);
  }, []);
  useEffect(() => {
    if (!notice) return;
    const id = setTimeout(() => setNotice(""), 4500);
    return () => clearTimeout(id);
  }, [notice]);
  return (
    <Auth.Provider
      value={{
        user,
        token,
        login: (data) => {
          setUser(data.user);
          setToken(data.access_token);
        },
        logout,
      }}
    >
      <Notice.Provider value={setNotice}>
        <a className="skip-link" href="#main">
          Saltar al contenido
        </a>
        <Header />
        <main id="main">
          <Routes>
            <Route path="/" element={<Catalog />} />
            <Route path="/productos/:id" element={<ProductDetail />} />
            {[
              ["acceso", "login"],
              ["registro", "register"],
              ["recuperar", "forgot"],
              ["restablecer", "reset"],
            ].map(([path, kind]) => (
              <Route
                key={kind}
                path={"/" + path}
                element={<AuthPage key={kind} kind={kind} />}
              />
            ))}
            <Route
              path="/carrito"
              element={
                <Guard>
                  <CartPage />
                </Guard>
              }
            />
            <Route
              path="/pedidos"
              element={
                <Guard>
                  <OrdersPage />
                </Guard>
              }
            />
            <Route
              path="/pedidos/:id"
              element={
                <Guard>
                  <OrderDetail />
                </Guard>
              }
            />
            <Route
              path="/perfil"
              element={
                <Guard>
                  <Profile />
                </Guard>
              }
            />
            <Route
              path="/admin"
              element={
                <Guard admin>
                  <Admin />
                </Guard>
              }
            />
            <Route
              path="*"
              element={
                <div className="page empty">
                  <h1>Esta página no está aquí.</h1>
                  <Link className="button primary" to="/">
                    Volver a la tienda
                  </Link>
                </div>
              }
            />
          </Routes>
        </main>
        <footer className="footer">
          <Link className="logo" to="/">
            QuickShop<span className="logo-dot">.</span>
          </Link>
          <span>Lo esencial, bien elegido.</span>
          <small>Proyecto de formación · Sin pagos reales</small>
        </footer>
        {notice && (
          <div className="toast" role="status">
            <Icon name="check" size={18} />
            {notice}
            <button aria-label="Cerrar aviso" onClick={() => setNotice("")}>
              <Icon name="close" size={15} />
            </button>
          </div>
        )}
      </Notice.Provider>
    </Auth.Provider>
  );
}
export default function App() {
  return (
    <BrowserRouter>
      <Shell />
    </BrowserRouter>
  );
}
