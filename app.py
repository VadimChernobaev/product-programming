"""Учебный интерфейс управления процессами (Streamlit).

Запуск: streamlit run app.py
Выполнение процессов в этой версии имитируется: пользователь завершает их вручную.
"""
import streamlit as st

from src.orchestrator import Orchestrator, Status
from src.simulator import add_demo_scenario

st.set_page_config(page_title="Оркестратор рисков", layout="wide")
st.title("Оркестратор процессов оценки рисков")
st.caption("MVP: контроль ресурсных конфликтов и очередь; без реальных вычислений.")

if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = Orchestrator()
orch = st.session_state.orchestrator

left, right = st.columns(2)
with left:
    with st.form("new_process"):
        name = st.text_input("Название процесса", "Оценка кредитного риска")
        day = st.date_input("Дата данных")
        resources = st.text_input("Ресурсы через запятую", "portfolio:demo")
        submit = st.form_submit_button("Добавить процесс")
    if submit:
        try:
            process_id = orch.submit(name, str(day), resources.split(","))
            st.success(f"Задача {process_id[:8]} добавлена")
        except ValueError as exc:
            st.error(str(exc))
with right:
    st.subheader("Демонстрация")
    if st.button("Добавить четыре тестовых процесса"):
        add_demo_scenario(orch)
        st.rerun()
    if st.button("Очистить сценарий"):
        st.session_state.orchestrator = Orchestrator()
        st.rerun()

snapshot = orch.snapshot()
st.subheader("Очередь и статусы")
if snapshot:
    st.dataframe(
        [{**row, "id": row["id"][:8]} for row in snapshot],
        use_container_width=True,
        hide_index=True,
    )
    running = [row for row in snapshot if row["Статус"] == Status.RUNNING.value]
    if running:
        selected_id = st.selectbox(
            "Завершить выполняющийся процесс",
            options=[row["id"] for row in running],
            format_func=lambda pid: next(
                f'{row["Процесс"]} — {pid[:8]}' for row in running if row["id"] == pid
            ),
        )
        col_done, col_fail = st.columns(2)
        if col_done.button("Завершить успешно"):
            orch.complete(selected_id)
            st.rerun()
        if col_fail.button("Завершить с ошибкой"):
            orch.complete(selected_id, success=False)
            st.rerun()
else:
    st.info("Пока нет процессов. Добавьте процесс или запустите демонстрацию.")

st.caption("Внимание: состояние хранится в сессии интерфейса. "
           "Для многопользовательской версии необходим общий серверный оркестратор.")
