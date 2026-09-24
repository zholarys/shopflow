import { useState, useEffect } from "react";
import axios from "axios";

const api = axios.create({ baseURL: "/api" });

export default function App() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [cart, setCart] = useState([]);
  const [token, setToken] = useState(null);
  const [view, setView] = useState("shop");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [search, setSearch] = useState("");
  const [activeCategory, setActiveCategory] = useState(null);

  useEffect(() => {
    api.get("/products/categories").then(r => setCategories(r.data));
  }, []);

  useEffect(() => {
    const params = {};
    if (search) params.search = search;
    if (activeCategory) params.category = activeCategory;
    api.get("/products/", { params }).then(r => setProducts(r.data));
  }, [search, activeCategory]);

  const login = async () => {
    try {
      const r = await api.post("/auth/login", { email, password });
      setToken(r.data.access_token);
      setView("shop");
      setMessage("Logged in!");
    } catch {
      setMessage("Invalid credentials");
    }
  };

  const register = async () => {
    try {
      await api.post("/auth/register", { email, password });
      setMessage("Registered! Now login.");
    } catch (e) {
      setMessage(e.response?.data?.detail || "Error");
    }
  };

  const addToCart = (product) => {
    setCart(c => {
      const ex = c.find(i => i.product_id === product.id);
      if (ex) return c.map(i => i.product_id === product.id ? {...i, quantity: i.quantity + 1} : i);
      return [...c, { product_id: product.id, quantity: 1, name: product.name, price: product.price }];
    });
  };

  const placeOrder = async () => {
    if (!token) { setMessage("Please login first"); setView("login"); return; }
    try {
      const r = await api.post("/orders/", {
        items: cart.map(i => ({ product_id: i.product_id, quantity: i.quantity }))
      }, { headers: { Authorization: `Bearer ${token}` } });
      setMessage(`Order #${r.data.id} placed! Payment: ${r.data.payment_id}`);
      setCart([]);
      setView("shop");
    } catch (e) {
      setMessage(e.response?.data?.detail || "Order failed");
    }
  };

  const total = cart.reduce((s, i) => s + i.price * i.quantity, 0);

  return (
    <div style={{ fontFamily: "sans-serif", maxWidth: 960, margin: "0 auto", padding: 20 }}>
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "2px solid #333", paddingBottom: 10, marginBottom: 20 }}>
        <h1 style={{ margin: 0 }}>⚡ ShopFlow</h1>
        <nav style={{ display: "flex", gap: 12, alignItems: "center" }}>
          <button onClick={() => setView("shop")}>Shop</button>
          <button onClick={() => setView("cart")}>Cart ({cart.length})</button>
          {token ? <span style={{ color: "green" }}>✓ Logged in</span> : <button onClick={() => setView("login")}>Login</button>}
        </nav>
      </header>

      {message && (
        <div style={{ background: "#e8f5e9", border: "1px solid #4caf50", padding: 10, marginBottom: 15, borderRadius: 4 }}>
          {message} <button onClick={() => setMessage("")}>×</button>
        </div>
      )}

      {view === "shop" && (
        <>
          <div style={{ display: "flex", gap: 10, marginBottom: 16, flexWrap: "wrap", alignItems: "center" }}>
            <input
              placeholder="🔍 Search products..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              style={{ padding: "8px 12px", fontSize: 15, borderRadius: 6, border: "1px solid #ccc", flex: 1, minWidth: 200 }}
            />
            <button
              onClick={() => setActiveCategory(null)}
              style={{ padding: "8px 14px", borderRadius: 6, border: "1px solid #333", background: activeCategory === null ? "#333" : "#fff", color: activeCategory === null ? "#fff" : "#333", cursor: "pointer" }}
            >
              All
            </button>
            {categories.map(cat => (
              <button
                key={cat}
                onClick={() => setActiveCategory(activeCategory === cat ? null : cat)}
                style={{ padding: "8px 14px", borderRadius: 6, border: "1px solid #333", background: activeCategory === cat ? "#333" : "#fff", color: activeCategory === cat ? "#fff" : "#333", cursor: "pointer", textTransform: "capitalize" }}
              >
                {cat}
              </button>
            ))}
          </div>

          <p style={{ color: "#666", marginBottom: 12 }}>{products.length} product{products.length !== 1 ? "s" : ""} found</p>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 20 }}>
            {products.map(p => (
              <div key={p.id} style={{ border: "1px solid #ddd", borderRadius: 8, padding: 16 }}>
                <img src={p.image_url} alt={p.name} style={{ width: "100%", borderRadius: 4 }} />
                <h3 style={{ margin: "10px 0 4px" }}>{p.name}</h3>
                <p style={{ color: "#666", fontSize: 13, margin: "0 0 8px" }}>{p.description}</p>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <strong>${p.price}</strong>
                  <button onClick={() => addToCart(p)} style={{ background: "#333", color: "#fff", border: "none", padding: "6px 12px", borderRadius: 4, cursor: "pointer" }}>
                    Add to cart
                  </button>
                </div>
                <small style={{ color: "#999" }}>Stock: {p.stock}</small>
              </div>
            ))}
            {products.length === 0 && (
              <div style={{ gridColumn: "1/-1", textAlign: "center", padding: 40, color: "#999" }}>
                No products found
              </div>
            )}
          </div>
        </>
      )}

      {view === "cart" && (
        <div>
          <h2>Cart</h2>
          {cart.length === 0 ? <p>Empty</p> : (
            <>
              {cart.map(i => (
                <div key={i.product_id} style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid #eee" }}>
                  <span>{i.name} × {i.quantity}</span>
                  <span>${(i.price * i.quantity).toFixed(2)}</span>
                </div>
              ))}
              <div style={{ marginTop: 16, fontWeight: "bold" }}>Total: ${total.toFixed(2)}</div>
              <button onClick={placeOrder} style={{ marginTop: 12, background: "#4caf50", color: "#fff", border: "none", padding: "10px 24px", borderRadius: 4, cursor: "pointer", fontSize: 16 }}>
                Place Order
              </button>
            </>
          )}
        </div>
      )}

      {view === "login" && (
        <div style={{ maxWidth: 360 }}>
          <h2>Login / Register</h2>
          <input placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} style={{ display: "block", width: "100%", marginBottom: 8, padding: 8, boxSizing: "border-box" }} />
          <input placeholder="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} style={{ display: "block", width: "100%", marginBottom: 12, padding: 8, boxSizing: "border-box" }} />
          <button onClick={login} style={{ marginRight: 8 }}>Login</button>
          <button onClick={register}>Register</button>
        </div>
      )}
    </div>
  );
}
