"""
PlacidWay AI Healthcare Navigator - Official Assessment Demo
Interactive Chatbot grounded exclusively on verified PlacidWay knowledge pages.
"""

import streamlit as st
import time
import os
import json
from rag.bot_engine import PlacidWayBotEngine
from ingestion.scraper import crawl_knowledge_base, APPROVED_SOURCES
from ingestion.chunker import build_chunked_index

# Page Configuration
st.set_page_config(
    page_title="PlacidWay AI Healthcare Navigator",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling to match PlacidWay Healthcare Branding (Blue / Teal theme)
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0b5c9e;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #555;
        margin-bottom: 20px;
    }
    .stChatMessage {
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 10px;
    }
    .source-box {
        background-color: rgba(11, 92, 158, 0.12);
        border-left: 4px solid #0b5c9e;
        padding: 10px 14px;
        border-radius: 6px;
        font-size: 0.9rem;
        margin-top: 10px;
    }
    .source-box a {
        color: #1a8cff;
        word-break: break-all;
    }
    .disclaimer-box {
        background-color: #fff9e6;
        border-left: 4px solid #f39c12;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 0.82rem;
        color: #7f5200;
        margin-top: 10px;
    }
    .badge-status {
        background-color: #e8f8f5;
        color: #117a65;
        padding: 4px 10px;
        border-radius: 15px;
        font-weight: 600;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! I am the **PlacidWay AI Healthcare Assistant**.\n\n"
                "I am grounded exclusively on verified medical tourism data for **Immunity Therapy Center (ITC) in Tijuana, Mexico** and global alternative medicine costs. "
                "You can ask me about treatments (e.g. Adenocarcinoma, Adrenal, Anal Cancer), package inclusions, physician details, or pricing comparisons."
            ),
            "sources": ["https://www.placidway.com/profile/5/Alternative-Cancer-Treatment-by-ITC-Immunity-Therapy-Center"],
            "disclaimer": False
        }
    ]

@st.cache_resource
def get_engine():
    return PlacidWayBotEngine()

bot = get_engine()

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.markdown("### 🏥 **PlacidWay Portal**")
    st.markdown("<span class='badge-status'>● Knowledge Base Active (7 Pages)</span>", unsafe_allow_html=True)
    st.caption("AI Automation Engineer Assessment Submission")
    
    st.divider()
    
    # 1. Quick Test Prompts (1-Click Evaluation Rubric Testers)
    st.subheader("⚡ Quick Test Prompts")
    st.caption("Click to evaluate against the 8 assessment criteria:")
    
    test_prompts = [
        ("💰 Cost ($18,995 USD)", "How much does Alternative Adenocarcinoma Cancer Treatment cost in Mexico?"),
        ("⚖️ Comparison (Strict)", "Is Alternative Cancer Treatment cheaper in Mexico or Turkey?"),
        ("📦 Package Inclusions", "What is included in the Alternative Cancer Treatment package?"),
        ("⏱️ Follow-up (Context)", "And what about recovery time?"),
        ("📅 Booking (Out of Scope)", "Can you book me an appointment for tomorrow?"),
        ("☀️ Scope (Weather)", "What is the weather in Cancun?"),
        ("🩺 Medical Advice Guard", "Is this surgery safe for my diabetes?"),
        ("🛑 Trick Question ($50)", "I heard it costs $50. Confirm that.")
    ]
    
    for label, query in test_prompts:
        if st.button(label, use_container_width=True):
            st.session_state.pending_query = query
            st.rerun()
            
    st.divider()
    
    # 2. Refresh / Re-index Feature
    st.subheader("🔄 Refresh Content")
    st.caption("Re-crawls the 7 approved pages & rebuilds index:")
    if st.button("Re-crawl & Update Knowledge Base", use_container_width=True):
        with st.spinner("Politely crawling 7 PlacidWay pages (~1 req/sec)..."):
            base_dir = os.path.dirname(__file__)
            kb_path = os.path.join(base_dir, 'data', 'knowledge_base.json')
            chunks_path = os.path.join(base_dir, 'data', 'chunks.json')
            crawl_knowledge_base(kb_path)
            build_chunked_index(kb_path, chunks_path)
            st.cache_resource.clear()
            st.success("Knowledge Base successfully updated and re-indexed!")
            time.sleep(1)
            st.rerun()

    # 3. Lead Capture Form
    st.divider()
    st.subheader("📋 Request a Free Quote")
    with st.expander("Patient Inquiry & Quote Form", expanded=False):
        lead_name = st.text_input("Full Name", key="l_name")
        lead_email = st.text_input("Email Address", key="l_email")
        lead_treatment = st.selectbox("Treatment of Interest", [
            "Alternative Cancer Treatment (ITC)",
            "Adenocarcinoma Package",
            "Adrenal Cancer Package",
            "Anal Cancer Package",
            "Other Alternative Medicine"
        ], key="l_treat")
        if st.button("Submit Quote Request"):
            if lead_name and lead_email:
                bot.log_lead(lead_name, lead_email, treatment=lead_treatment)
                st.success("Thank you! A PlacidWay care coordinator will reach out shortly.")
            else:
                st.warning("Please provide your name and email.")

    # 4. Content Gap Monitoring
    st.divider()
    with st.expander("🔍 Content Gap Logs", expanded=False):
        gaps_path = os.path.join(os.path.dirname(__file__), 'data', 'content_gaps.json')
        if os.path.exists(gaps_path):
            try:
                with open(gaps_path, 'r', encoding='utf-8') as f:
                    gaps_data = json.load(f)
                st.write(f"Logged Gaps: **{len(gaps_data)}**")
                for item in gaps_data[-5:]:
                    st.markdown(f"• **Q:** {item['question']}\n  *Reason:* {item.get('reason','')}")
            except Exception:
                st.write("No gaps logged yet.")
        else:
            st.write("No gaps logged yet.")

# --- MAIN CONTENT & CHAT ---
st.markdown("<div class='main-header'>PlacidWay AI Healthcare Navigator</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Verified Clinical Knowledge • Zero Hallucinations • Strict Medical Grounding</div>", unsafe_allow_html=True)

# Display Chat History
for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]
    sources = message.get("sources", [])
    disclaimer = message.get("disclaimer", False)
    
    with st.chat_message(role, avatar="🧑‍⚕️" if role == "assistant" else "👤"):
        st.markdown(content)
        
        # Display clickable source citations
        if role == "assistant" and sources:
            st.markdown("<div class='source-box'><b>Verified Sources:</b><br>" + 
                        "<br>".join([f"• <a href='{u}' target='_blank'>{u}</a>" for u in sources]) + 
                        "</div>", unsafe_allow_html=True)
                        
        # Display medical disclaimer when relevant
        if role == "assistant" and disclaimer:
            st.markdown(
                "<div class='disclaimer-box'><b>Medical Disclaimer:</b> "
                "This information is for educational purposes based on PlacidWay provider listings and does not substitute professional medical diagnosis, advice, or treatment. Always consult a qualified oncologist or physician.</div>",
                unsafe_allow_html=True
            )

# Handle Pending Query (from Sidebar buttons) or User Chat Input
user_query = None
if "pending_query" in st.session_state and st.session_state.pending_query:
    user_query = st.session_state.pending_query
    st.session_state.pending_query = None
else:
    user_query = st.chat_input("Ask about treatment costs, ITC package inclusions, doctor background...")

if user_query:
    # Append User Message
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_query)
        
    # Generate Assistant Response
    with st.chat_message("assistant", avatar="🧑‍⚕️"):
        with st.spinner("Verifying PlacidWay knowledge pages..."):
            history_for_bot = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[:-1]]
            output = bot.answer_question(user_query, chat_history=history_for_bot)
            
            resp_content = output.get("response", "")
            sources = output.get("source_urls", [])
            disclaimer = output.get("disclaimer", False)
            
            st.markdown(resp_content)
            
            if sources:
                st.markdown("<div class='source-box'><b>Verified Sources:</b><br>" + 
                            "<br>".join([f"• <a href='{u}' target='_blank'>{u}</a>" for u in sources]) + 
                            "</div>", unsafe_allow_html=True)
                            
            if disclaimer:
                st.markdown(
                    "<div class='disclaimer-box'><b>Medical Disclaimer:</b> "
                    "This information is for educational purposes based on PlacidWay provider listings and does not substitute professional medical diagnosis, advice, or treatment. Always consult a qualified oncologist or physician.</div>",
                    unsafe_allow_html=True
                )
                
            st.session_state.messages.append({
                "role": "assistant",
                "content": resp_content,
                "sources": sources,
                "disclaimer": disclaimer
            })
