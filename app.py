import streamlit as st
import zipfile, os, shutil, base64, math
from utils import slugify
from github_utils import upload_file, list_files, delete_file
from firestore_utils import db
from settings import ADMIN_PASSWORD, BASE_URL

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Brainsta Game Admin",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =====================================================
# CUSTOM CSS
# =====================================================
st.markdown("""
<style>
    /* Main container styling */
    .main {
        padding: 2rem;
    }
    
    /* Header styling */
    .admin-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .admin-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .admin-header p {
        color: rgba(255, 255, 255, 0.9);
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
    }
    
    /* Card styling */
    .custom-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    
    .custom-card:hover {
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
    }
    
    /* Game item styling */
    .game-item {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        transition: all 0.2s ease;
    }
    
    .game-item:hover {
        background: white;
        border-color: #667eea;
    }
    
    /* Badge styling */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.875rem;
        font-weight: 500;
        margin-right: 0.5rem;
    }
    
    .badge-published {
        background: #d1fae5;
        color: #065f46;
    }
    
    .badge-draft {
        background: #fee2e2;
        color: #991b1b;
    }
    
    .badge-category {
        background: #dbeafe;
        color: #1e40af;
    }
    
    /* Button improvements */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
    
    /* Stats card */
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .stats-number {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
    }
    
    .stats-label {
        font-size: 0.875rem;
        opacity: 0.9;
        margin-top: 0.5rem;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #667eea;
    }
    
    /* Login page */
    .login-container {
        max-width: 400px;
        margin: 5rem auto;
        padding: 2rem;
        background: white;
        border-radius: 12px;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    }
    
    /* Pagination */
    .pagination {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 1rem;
        padding: 1rem;
        background: #f9fafb;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Checkbox alignment */
    .stCheckbox {
        padding-top: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================
# ADMIN LOGIN
# =====================================================
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("""
        <div class="login-container">
            <h1 style="text-align: center; color: #667eea;">🔐</h1>
            <h2 style="text-align: center; color: #1f2937;">Brainsta Admin</h2>
            <p style="text-align: center; color: #6b7280;">Please enter your credentials</p>
        </div>
    """, unsafe_allow_html=True)
    
    pwd = st.text_input("Password", type="password", placeholder="Enter admin password")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Login", use_container_width=True):
            if pwd == ADMIN_PASSWORD:
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("❌ Invalid password")
    st.stop()

# =====================================================
# HEADER
# =====================================================
st.markdown("""
    <div class="admin-header">
        <h1>🎮 Brainsta Game Admin Portal</h1>
        <p>Manage your game library with ease</p>
    </div>
""", unsafe_allow_html=True)

# =====================================================
# LOAD CATEGORIES & STATS
# =====================================================
categories_docs = list(db.collection("categories").stream())
categories = {c.id: c.to_dict().get("name", "Unnamed") for c in categories_docs}

all_games = list(db.collection("games").stream())
published_count = sum(1 for g in all_games if g.to_dict().get("published", False))

# Stats Dashboard
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{len(all_games)}</div>
            <div class="stats-label">Total Games</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="stats-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <div class="stats-number">{published_count}</div>
            <div class="stats-label">Published</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="stats-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <div class="stats-number">{len(all_games) - published_count}</div>
            <div class="stats-label">Drafts</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="stats-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
            <div class="stats-number">{len(categories)}</div>
            <div class="stats-label">Categories</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================
# ADD CATEGORY
# =====================================================
with st.expander("📂 Manage Categories", expanded=False):
    col1, col2 = st.columns([3, 1])
    new_cat = col1.text_input("New Category Name", placeholder="e.g., Puzzle, Action, Strategy")
    if col2.button("➕ Add", use_container_width=True):
        if new_cat.strip():
            db.collection("categories").add({"name": new_cat.strip()})
            st.success("✅ Category added successfully")
            st.rerun()
        else:
            st.warning("⚠️ Please enter a category name")

# =====================================================
# UPLOAD GAME
# =====================================================
st.markdown('<div class="section-header">⬆️ Upload New Game</div>', unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        title = st.text_input("Game Title", placeholder="Enter game title")
        zip_file = st.file_uploader("Game ZIP File", type=["zip"], help="Upload a ZIP file containing your game")
    
    with col2:
        category_id = st.selectbox(
            "Category",
            options=list(categories.keys()),
            format_func=lambda x: categories[x] if x in categories else "Uncategorized"
        )
        st.markdown("<br>", unsafe_allow_html=True)
        upload_btn = st.button("🚀 Upload Game", use_container_width=True, type="primary")
    
    st.markdown('</div>', unsafe_allow_html=True)

if upload_btn:
    if not title or not zip_file:
        st.error("❌ Title and ZIP file are required")
        st.stop()

    titles = [d.to_dict().get("title", "").lower() for d in db.collection("games").stream()]
    if title.lower() in titles:
        st.error("❌ A game with this title already exists")
        st.stop()

    with st.spinner("⏳ Uploading game... Please wait"):
        slug = slugify(title)
        
        # Ensure tmp directory exists first
        if not os.path.exists("tmp"):
            os.makedirs("tmp")
        
        tmp_dir = f"tmp/{slug}"
        os.makedirs(tmp_dir, exist_ok=True)

        zip_path = f"{tmp_dir}.zip"
        with open(zip_path, "wb") as f:
            f.write(zip_file.read())

        with zipfile.ZipFile(zip_path) as z:
            z.extractall(tmp_dir)

        for root, _, files in os.walk(tmp_dir):
            for file in files:
                full = os.path.join(root, file)
                rel = f"{slug}/" + os.path.relpath(full, tmp_dir)
                with open(full, "rb") as f:
                    upload_file(rel, base64.b64encode(f.read()).decode())

        url = f"{BASE_URL}/{slug}/index.html"

        db.collection("games").add({
            "title": title,
            "titleNormalized": title.lower(),
            "slug": slug,
            "categoryId": category_id,
            "url": url,
            "published": False
        })

        shutil.rmtree(tmp_dir)
        os.remove(zip_path)

        st.success("✅ Game uploaded successfully!")
        st.balloons()

# =====================================================
# SEARCH & PAGINATION
# =====================================================
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-header">🎯 Manage Games</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([3, 1, 1])
search = col1.text_input("🔍 Search", placeholder="Search by title or slug")
page_size = col2.selectbox("Items per page", [5, 10, 20, 50], index=1)

if "page" not in st.session_state:
    st.session_state.page = 1

docs = list(db.collection("games").stream())
docs.sort(key=lambda d: d.id, reverse=True)

if search:
    docs = [
        d for d in docs
        if search.lower() in d.to_dict().get("title", "").lower()
        or search.lower() in d.to_dict().get("slug", "").lower()
    ]

total = len(docs)
total_pages = max(1, math.ceil(total / page_size))

st.session_state.page = max(1, min(st.session_state.page, total_pages))
start = (st.session_state.page - 1) * page_size
end = start + page_size
page_docs = docs[start:end]

# =====================================================
# PAGINATION CONTROLS
# =====================================================
if total > 0:
    st.markdown('<div class="pagination">', unsafe_allow_html=True)
    p1, p2, p3 = st.columns([1, 2, 1])

    if p1.button("⬅ Previous", disabled=st.session_state.page == 1, use_container_width=True):
        st.session_state.page -= 1
        st.rerun()

    p2.markdown(
        f"<div style='text-align:center; padding-top: 0.5rem; font-weight: 600;'>Page {st.session_state.page} of {total_pages} ({total} games)</div>",
        unsafe_allow_html=True
    )

    if p3.button("Next ➡", disabled=st.session_state.page == total_pages, use_container_width=True):
        st.session_state.page += 1
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# GAME LIST + BULK DELETE
# =====================================================
selected = set()

if total == 0:
    st.info("📭 No games found. Upload your first game to get started!")
else:
    for g in page_docs:
        data = g.to_dict()
        slug = data.get("slug", slugify(data.get("title", "")))
        cat = categories.get(data.get("categoryId"), "Uncategorized")
        is_published = data.get("published", False)

        st.markdown('<div class="game-item">', unsafe_allow_html=True)
        
        c1, c2, c3, c4, c5 = st.columns([0.4, 3.6, 1.5, 1, 1.5])

        sel = c1.checkbox("", key=f"sel_{g.id}", label_visibility="collapsed")
        if sel:
            selected.add(g.id)

        with c2:
            st.markdown(f"### 🎮 {data.get('title')}")
            badge_class = "badge-published" if is_published else "badge-draft"
            status = "Published" if is_published else "Draft"
            st.markdown(
                f'<span class="badge {badge_class}">● {status}</span>'
                f'<span class="badge badge-category">📂 {cat}</span>'
                f'<code style="font-size: 0.8rem; color: #6b7280;">{slug}</code>',
                unsafe_allow_html=True
            )

        pub = c3.checkbox(
            "✓ Publish",
            value=is_published,
            key=f"pub_{g.id}"
        )
        if pub != is_published:
            db.collection("games").document(g.id).update({"published": pub})
            st.rerun()

        if c4.button("👁", key=f"prev_{g.id}", use_container_width=True, help="Preview game"):
            st.components.v1.iframe(data["url"], height=600, scrolling=True)

        if c5.button("🗑 Delete", key=f"del_{g.id}", use_container_width=True, type="secondary"):
            files = list_files(slug)
            for f in files:
                delete_file(f["path"], f["sha"])
            db.collection("games").document(g.id).delete()
            st.success("✅ Game deleted successfully")
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# BULK DELETE
# =====================================================
if selected:
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button(f"🧹 Delete {len(selected)} Selected Game(s)", use_container_width=True, type="primary"):
            with st.spinner("Deleting selected games..."):
                for game_id in selected:
                    doc = db.collection("games").document(game_id).get()
                    data = doc.to_dict()
                    slug = data.get("slug", slugify(data.get("title", "")))

                    files = list_files(slug)
                    for f in files:
                        delete_file(f["path"], f["sha"])

                    db.collection("games").document(game_id).delete()

            st.success(f"✅ {len(selected)} game(s) deleted successfully")
            st.rerun()

# =====================================================
# FOOTER
# =====================================================
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
    <div style="text-align: center; padding: 2rem; color: #6b7280; font-size: 0.875rem;">
        <p>Brainsta Game Admin Portal | Powered by Streamlit</p>
    </div>
""", unsafe_allow_html=True)