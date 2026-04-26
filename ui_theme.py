import streamlit as st


def inject_styles():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

        :root {
            --bg: #090b12;
            --bg-2: #0d1220;
            --panel: rgba(15, 20, 35, 0.88);
            --panel-strong: rgba(20, 27, 46, 0.96);
            --panel-soft: rgba(14, 18, 31, 0.78);
            --ink: #edf2ff;
            --muted: #b5c0df;
            --line: rgba(129, 145, 187, 0.22);
            --brand: #6ea8fe;
            --brand-2: #34d3b4;
            --warm: #ffb86b;
            --danger: #ff6b81;
            --success: #48e5a0;
            --shadow: 0 18px 42px rgba(0, 0, 0, 0.34);
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(110, 168, 254, 0.18), transparent 28%),
                radial-gradient(circle at top right, rgba(52, 211, 180, 0.12), transparent 26%),
                linear-gradient(180deg, #090b12 0%, #0c1120 100%);
            color: var(--ink);
        }

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', sans-serif;
            color: var(--ink);
        }

        body, p, li, label, .stMarkdown, .stText, .stCaption {
            color: var(--ink);
        }

        h1, h2, h3, h4 {
            font-family: 'Manrope', sans-serif;
            color: var(--ink);
            letter-spacing: -0.03em;
        }

        .block-container {
            padding-top: 0.8rem;
            padding-bottom: 3rem;
            max-width: 1240px;
        }

        header[data-testid="stHeader"] {
            background: transparent !important;
            height: 0 !important;
            min-height: 0 !important;
            display: none !important;
        }

        .stAppToolbar,
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"] {
            display: none !important;
        }

        div[data-testid="stSidebar"] {
            background:
                linear-gradient(180deg, rgba(12, 17, 31, 0.98), rgba(9, 12, 22, 0.98));
            border-right: 1px solid var(--line);
        }

        div[data-testid="stSidebar"] > div:first-child {
            background:
                linear-gradient(180deg, rgba(12, 17, 31, 0.98), rgba(9, 12, 22, 0.98)) !important;
        }

        section[data-testid="stSidebar"] {
            background:
                linear-gradient(180deg, rgba(12, 17, 31, 0.98), rgba(9, 12, 22, 0.98)) !important;
        }

        .hero-card, .panel-card, .metric-card, .repo-card, .soft-card, .queue-card, .task-card, .leader-card {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 24px;
            box-shadow: var(--shadow);
            backdrop-filter: blur(14px);
        }

        .insight-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 12px;
            margin-bottom: 14px;
        }

        .insight-card {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 20px;
            padding: 16px;
        }

        .insight-card .title {
            font-family: 'Manrope', sans-serif;
            font-size: 0.92rem;
            font-weight: 800;
            color: var(--ink);
        }

        .insight-card .text {
            margin-top: 6px;
            color: var(--muted);
            font-size: 0.84rem;
            line-height: 1.5;
        }

        .hero-card {
            padding: 30px 30px 28px;
            background:
                radial-gradient(circle at top right, rgba(110, 168, 254, 0.16), transparent 35%),
                linear-gradient(135deg, rgba(255, 255, 255, 0.02), rgba(52, 211, 180, 0.08));
            margin-bottom: 18px;
        }

        .hero-title {
            font-size: 2.4rem;
            font-weight: 800;
            line-height: 1.02;
            margin-top: 8px;
            max-width: 12ch;
        }

        .hero-subtitle {
            color: var(--muted);
            margin-top: 8px;
            font-size: 1rem;
            max-width: 64ch;
        }

        .hero-note {
            margin-top: 14px;
            color: #dfe8ff;
            font-size: 0.95rem;
        }

        .eyebrow {
            text-transform: uppercase;
            letter-spacing: 0.16em;
            font-size: 0.72rem;
            color: var(--brand);
            font-weight: 800;
        }

        .panel-card, .soft-card, .queue-card, .task-card, .leader-card {
            padding: 18px 20px;
            margin-bottom: 14px;
        }

        .metric-card {
            padding: 20px 18px 16px;
            min-height: 124px;
            background:
                linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01)),
                rgba(12, 17, 31, 0.9);
        }

        .metric-value {
            font-family: 'Manrope', sans-serif;
            font-size: 2rem;
            font-weight: 800;
            line-height: 1.05;
            color: var(--ink);
        }

        .metric-label {
            margin-top: 8px;
            font-size: 0.76rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: var(--muted);
        }

        .metric-note {
            margin-top: 8px;
            color: var(--brand-2);
            font-size: 0.78rem;
            font-weight: 700;
        }

        .mini-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 12px;
            margin-top: 18px;
        }

        .mini-card {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 18px;
            padding: 14px 15px;
            color: var(--muted);
        }

        .mini-card b {
            display: block;
            margin-bottom: 4px;
            color: var(--ink);
            font-family: 'Manrope', sans-serif;
        }

        .section-label {
            margin: 26px 0 12px;
            font-size: 0.76rem;
            letter-spacing: 0.16em;
            text-transform: uppercase;
            color: var(--brand);
            font-weight: 800;
        }

        .profile-row {
            display: flex;
            gap: 14px;
            align-items: center;
        }

        .avatar {
            width: 42px;
            height: 42px;
            border-radius: 999px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 800;
            font-family: 'Manrope', sans-serif;
            flex-shrink: 0;
            box-shadow: 0 10px 24px rgba(0, 0, 0, 0.32);
        }

        .pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 5px 10px;
            border-radius: 999px;
            background: rgba(255,255,255,0.05);
            color: var(--ink);
            font-size: 0.74rem;
            font-weight: 700;
            border: 1px solid rgba(255,255,255,0.08);
        }

        .tag {
            display: inline-flex;
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 700;
            margin-right: 6px;
        }

        .bar-row {
            margin-bottom: 14px;
        }

        .bar-head {
            display: flex;
            justify-content: space-between;
            font-size: 0.86rem;
            margin-bottom: 6px;
            color: #dbe5ff;
        }

        .bar-track {
            width: 100%;
            height: 9px;
            background: rgba(255,255,255,0.06);
            border-radius: 999px;
            overflow: hidden;
        }

        .bar-fill {
            height: 100%;
            border-radius: 999px;
            background: linear-gradient(90deg, var(--brand), var(--brand-2));
        }

        .repo-card {
            padding: 14px 16px;
            margin-bottom: 10px;
        }

        .repo-card a {
            color: #f2f6ff;
            text-decoration: none;
            font-weight: 700;
        }

        .repo-meta {
            color: var(--muted);
            font-size: 0.82rem;
            margin-top: 4px;
        }

        .invite-box {
            background: linear-gradient(135deg, rgba(110,168,254,0.16), rgba(52,211,180,0.12));
            border: 1px dashed rgba(110,168,254,0.44);
            border-radius: 18px;
            padding: 16px;
            text-align: center;
            font-family: 'Manrope', sans-serif;
            font-weight: 800;
            letter-spacing: 0.18em;
            color: #dce9ff;
        }

        .empty {
            text-align: center;
            padding: 28px 22px;
            color: var(--muted);
            background: rgba(255,255,255,0.02);
            border: 1px dashed rgba(255,255,255,0.08);
            border-radius: 20px;
        }

        .stButton > button,
        div[data-testid="stFormSubmitButton"] > button {
            background: linear-gradient(135deg, #6ea8fe, #34d3b4);
            color: #06111d;
            border: none;
            border-radius: 14px;
            font-weight: 800;
            min-height: 2.8rem;
            box-shadow: 0 14px 26px rgba(45, 104, 214, 0.18);
        }

        .stButton > button:hover,
        div[data-testid="stFormSubmitButton"] > button:hover {
            opacity: 0.96;
        }

        .stTextInput input,
        .stTextArea textarea,
        .stDateInput input,
        .stNumberInput input,
        div[data-baseweb="input"] input,
        div[data-baseweb="base-input"] input {
            border-radius: 14px !important;
            background: rgba(10, 14, 24, 0.96) !important;
            color: #f4f7ff !important;
            -webkit-text-fill-color: var(--ink) !important;
            caret-color: #f4f7ff !important;
            border: 1px solid rgba(255,255,255,0.12) !important;
            box-shadow: none !important;
        }

        .stSelectbox div[data-baseweb="select"] > div {
            border-radius: 14px !important;
            background: rgba(10, 14, 24, 0.96) !important;
            color: var(--ink) !important;
            border: 1px solid rgba(255,255,255,0.12) !important;
        }

        .stTextInput input::placeholder,
        .stTextArea textarea::placeholder,
        .stNumberInput input::placeholder,
        div[data-baseweb="input"] input::placeholder,
        div[data-baseweb="base-input"] input::placeholder {
            color: #93a5d1 !important;
            opacity: 1 !important;
        }

        .stTextInput label,
        .stTextArea label,
        .stDateInput label,
        .stSelectbox label,
        .stNumberInput label,
        .stSlider label,
        .stRadio label,
        .stCheckbox label {
            color: #e5ecff !important;
        }

        .stSelectbox div[data-baseweb="select"] * {
            color: var(--ink) !important;
        }

        .stNumberInput input {
            background: rgba(10, 14, 24, 0.96) !important;
            color: #f4f7ff !important;
            -webkit-text-fill-color: #f4f7ff !important;
        }

        .stTextInput input:focus,
        .stTextArea textarea:focus,
        .stDateInput input:focus,
        .stNumberInput input:focus,
        div[data-baseweb="input"] input:focus,
        div[data-baseweb="base-input"] input:focus {
            border-color: rgba(110, 168, 254, 0.55) !important;
            box-shadow: 0 0 0 1px rgba(110, 168, 254, 0.25) !important;
            outline: none !important;
        }

        input:-webkit-autofill,
        input:-webkit-autofill:hover,
        input:-webkit-autofill:focus,
        textarea:-webkit-autofill,
        textarea:-webkit-autofill:focus,
        select:-webkit-autofill {
            -webkit-text-fill-color: #f4f7ff !important;
            -webkit-box-shadow: 0 0 0 1000px rgba(10, 14, 24, 0.96) inset !important;
            transition: background-color 9999s ease-in-out 0s !important;
            caret-color: #f4f7ff !important;
        }

        div[data-baseweb="input"],
        div[data-baseweb="base-input"] {
            background: rgba(10, 14, 24, 0.96) !important;
            border-radius: 14px !important;
        }

        .stExpander {
            border: 1px solid rgba(255,255,255,0.08) !important;
            border-radius: 18px !important;
            background: rgba(255,255,255,0.02) !important;
        }

        .stExpander summary,
        .stExpander details summary p {
            color: var(--ink) !important;
        }

        .stTabs [data-baseweb="tab"] p {
            color: inherit !important;
        }

        .stForm {
            background: rgba(255,255,255,0.015);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 18px;
            padding: 10px 10px 2px;
        }

        .stMetric {
            background: rgba(255,255,255,0.02);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 16px;
            padding: 10px 14px;
        }

        .stMetric label, .stMetric [data-testid="stMetricLabel"] {
            color: var(--muted) !important;
        }

        [data-testid="stSidebar"] .stRadio p,
        [data-testid="stSidebar"] .stMarkdown p,
        [data-testid="stSidebar"] label {
            color: #dce5ff !important;
        }

        section[data-testid="stSidebar"] * {
            color: #dce5ff;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] label {
            background: rgba(255,255,255,0.025) !important;
            border: 1px solid rgba(255,255,255,0.08) !important;
            border-radius: 14px !important;
            padding: 10px 12px !important;
            margin-bottom: 8px !important;
            display: flex !important;
            align-items: center !important;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
            background: rgba(110,168,254,0.08) !important;
            border-color: rgba(110,168,254,0.22) !important;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] label p {
            color: #dce5ff !important;
            font-weight: 700 !important;
            opacity: 1 !important;
            font-size: 1rem !important;
        }

        [data-testid="stSidebar"] input[type="radio"] {
            accent-color: #6ea8fe !important;
        }

        [data-testid="stSidebar"] [role="radiogroup"] {
            background: transparent !important;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] div {
            color: #dce5ff !important;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] label > div,
        [data-testid="stSidebar"] [data-testid="stRadio"] label span,
        [data-testid="stSidebar"] [data-testid="stRadio"] label p,
        [data-testid="stSidebar"] [data-testid="stRadio"] label div[data-testid="stMarkdownContainer"] p {
            color: #dce5ff !important;
            opacity: 1 !important;
            -webkit-text-fill-color: #dce5ff !important;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] label:hover p,
        [data-testid="stSidebar"] [data-testid="stRadio"] label:hover span,
        [data-testid="stSidebar"] [data-testid="stRadio"] label:hover div {
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }

        .stTabs [data-baseweb="tab"] {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 14px;
            color: var(--muted);
            padding: 10px 14px;
        }

        .stTabs [aria-selected="true"] {
            color: var(--ink) !important;
            border-color: rgba(110,168,254,0.34) !important;
        }

        .stAlert {
            background: rgba(16, 20, 36, 0.9) !important;
            color: var(--ink) !important;
            border: 1px solid rgba(255,255,255,0.08) !important;
            border-radius: 16px !important;
        }

        .stInfo, .stSuccess, .stWarning, .stError {
            color: var(--ink) !important;
        }

        code {
            color: #d4f0ff !important;
            background: rgba(255,255,255,0.05) !important;
        }

        a {
            color: #8dc0ff !important;
        }

        label, .stMarkdown, p, span, div {
            color: inherit;
        }

        @media (max-width: 900px) {
            .hero-title {
                font-size: 1.8rem;
            }

            .mini-grid {
                grid-template-columns: 1fr;
            }

            .insight-grid {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
