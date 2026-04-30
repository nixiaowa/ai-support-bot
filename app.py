import streamlit as st
import os

st.set_page_config(page_title="智能问答助手")

# =========================
# 初始化聊天记录
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []

# =========================
# 读取知识库
# =========================
def load_qa():
    qa_pairs = []

    if not os.path.exists("knowledge/faq.txt"):
        return qa_pairs

    with open("knowledge/faq.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()

    q, a = None, None

    for line in lines:
        line = line.strip()

        if line.startswith("Q:"):
            q = line.replace("Q:", "").strip()
        elif line.startswith("A:"):
            a = line.replace("A:", "").strip()

            if q and a:
                qa_pairs.append((q, a))
                q, a = None, None

    return qa_pairs


qa_list = load_qa()

# =========================
# 保存知识库
# =========================
def save_qa(q, a):
    os.makedirs("knowledge", exist_ok=True)
    with open("knowledge/faq.txt", "a", encoding="utf-8") as f:
        f.write(f"\nQ: {q}\nA: {a}\n")

# =========================
# 🔥 稳定模糊匹配（核心）
# =========================
def find_answer(question):
    question = question.lower()
    question_words = set(question.split())

    best_match = None
    best_score = 0

    for q, a in qa_list:
        q_lower = q.lower()
        q_words = set(q_lower.split())

        # ① 完全包含（强匹配）
        if question in q_lower or q_lower in question:
            return a

        # ② 词重叠
        common_words = question_words & q_words

        # ③ 评分（稳定版）
        score = len(common_words)

        # ④ 归一化（防止长句占优）
        score = score / (len(q_words) + 1e-6)

        if score > best_score:
            best_score = score
            best_match = a

    # 🔥 阈值（关键：调低保证能匹配）
    if best_score > 0.05:
        return best_match

    return "暂无匹配答案，请补充知识库或换一种问法。"

# =========================
# UI
# =========================
menu = st.sidebar.selectbox("功能选择", ["💬 用户问答", "🛠 知识库后台"])

# =========================
# 前台：聊天
# =========================
if menu == "💬 用户问答":
    st.title("AI小助手")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_input = st.chat_input("请输入你的问题")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        answer = find_answer(user_input)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

        st.rerun()

# =========================
# 后台：知识库管理
# =========================
elif menu == "🛠 知识库后台":
    st.title("🛠 知识库管理后台")

    st.subheader("➕ 新增知识")

    q = st.text_input("问题")
    a = st.text_area("答案")

    if st.button("保存"):
        if q and a:
            save_qa(q, a)
            st.success("保存成功！")
            qa_list.append((q, a))  # 🔥 立即生效
        else:
            st.error("问题和答案不能为空")

    st.divider()

    st.subheader("📚 当前知识库")

    for q, a in qa_list:
        st.markdown(f"**Q:** {q}")
        st.markdown(f"**A:** {a}")
        st.markdown("---")
