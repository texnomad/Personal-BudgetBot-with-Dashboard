import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Путь к вашей базе данных
DB_PATH = r"C:\Docs\Python\PycharmProjects\PythonProject1\Budget_DB.db"

st.set_page_config(page_title="Бюджет", layout="wide")
st.title("📊 Визуализация бюджета")

@st.cache_data(ttl=60)
def load_data():
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql("SELECT * FROM records ORDER BY id DESC", conn)
        conn.close()
        if df.empty:
            return df
        df['date'] = pd.to_datetime(df['date'])
        df['month_label'] = df['date'].dt.strftime('%b %Y')
        df['year_month'] = df['date'].dt.to_period('M')
        df['is_income'] = df['amount'] < 0
        df['amount_abs'] = df['amount'].abs()
        return df
    except Exception as e:
        st.error(f"Ошибка загрузки данных: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("Нет данных в базе. Отправьте запись через Telegram-бота.")
else:
    # === Глобальный накопительный остаток — сразу под заголовком ===
    total_global_income = df[df['amount'] < 0]['amount'].abs().sum()
    total_global_expense = df[df['amount'] >= 0]['amount'].sum()
    global_balance = total_global_income - total_global_expense

    st.metric("💰 Накопительный остаток", f"{global_balance:.0f} ₽")

    # === Фильтры (месяц + категории) ===
    col_month, col_cats = st.columns([1, 2])
    with col_month:
        months = sorted(df['year_month'].unique(), reverse=True)
        month_labels = [m.strftime('%b %Y') for m in months]
        selected_month_str = st.selectbox("Месяц", month_labels)
        selected_month = pd.Period(selected_month_str, freq='M')
    with col_cats:
        all_categories = sorted(df['category'].unique())
        selected_cats = st.multiselect("Категории", all_categories, default=all_categories)

    # Фильтрация по месяцу и категориям
    filtered_df = df[df['year_month'] == selected_month].copy()
    if selected_cats:
        filtered_df = filtered_df[filtered_df['category'].isin(selected_cats)]

    if filtered_df.empty:
        st.warning("Нет записей за выбранный период.")
    else:
        # === Расчёт месячных значений ===
        income_df = filtered_df[filtered_df['is_income']]
        expense_df = filtered_df[~filtered_df['is_income']]
        total_income = income_df['amount_abs'].sum() if not income_df.empty else 0
        total_expense = expense_df['amount_abs'].sum() if not expense_df.empty else 0
        monthly_net = total_income - total_expense

        # === Сравнение с прошлым месяцем (по расходам) ===
        prev_month = selected_month - 1
        prev_expense_df = df[(df['year_month'] == prev_month) & (~df['is_income'])]
        prev_expense = prev_expense_df['amount_abs'].sum() if not prev_expense_df.empty else 0
        if prev_expense > 0:
            expense_delta = f"{((total_expense - prev_expense) / prev_expense * 100):+.1f}%"
        else:
            expense_delta = "—"

        # === Вкладки ===
        tab_overview, tab_incomes, tab_expenses, tab_data = st.tabs(["Обзор", "Доходы", "Расходы", "Данные"])

        # --- Вкладка 1: Обзор ---
        with tab_overview:
            st.subheader("Основные показатели")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Доходы", f"{total_income:.0f} ₽")
            with col2:
                st.metric("Расходы", f"{total_expense:.0f} ₽", delta="-")
            with col3:
                color = "normal" if monthly_net >= 0 else "inverse"
                st.metric("Остаток (месяц)", f"{monthly_net:.0f} ₽", delta=None, delta_color=color)

            st.metric("Расходы vs прошлый месяц", f"{total_expense:.0f} ₽", delta=expense_delta)

        # --- Вкладка 2: Доходы ---
        with tab_incomes:
            if not income_df.empty:
                income_by_cat = income_df.groupby('category')['amount_abs'].sum().sort_values(ascending=False)
                top5_income = income_by_cat.head(5)
                if len(income_by_cat) > 5:
                    other_sum = income_by_cat[5:].sum()
                    top5_income['Остальное'] = other_sum
                st.subheader("Топ-5 источников дохода")
                st.bar_chart(top5_income)

                daily_income = income_df.groupby(income_df['date'].dt.date)['amount_abs'].sum()
                st.subheader("Доходы по дням")
                st.line_chart(daily_income)
            else:
                st.info("Нет доходов за выбранный период.")

        # --- Вкладка 3: Расходы ---
        with tab_expenses:
            if not expense_df.empty:
                expense_by_cat = expense_df.groupby('category')['amount_abs'].sum().sort_values(ascending=False)
                top5_expense = expense_by_cat.head(5)
                if len(expense_by_cat) > 5:
                    other_sum = expense_by_cat[5:].sum()
                    top5_expense['Остальное'] = other_sum
                st.subheader("Топ-5 категорий расходов")
                st.bar_chart(top5_expense)

                daily_expense = expense_df.groupby(expense_df['date'].dt.date)['amount_abs'].sum()
                st.subheader("Траты по дням")
                st.line_chart(daily_expense)
            else:
                st.info("Нет расходов за выбранный период.")

        # --- Вкладка 4: Данные ---
        with tab_data:
            st.subheader("Подробные записи")
            display_df = filtered_df[['date', 'amount', 'category', 'comment', 'is_income']].copy()
            display_df['date'] = display_df['date'].dt.strftime('%d.%m.%Y')
            display_df['type'] = display_df['is_income'].map({True: 'Доход', False: 'Расход'})
            display_df = display_df.rename(columns={
                'date': 'Дата',
                'amount': 'Сумма',
                'category': 'Категория',
                'comment': 'Комментарий',
                'type': 'Тип'
            })
            st.dataframe(display_df[['Дата', 'Сумма', 'Категория', 'Тип', 'Комментарий']], width="stretch")