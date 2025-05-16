import streamlit as st
from streamlit_option_menu import option_menu
import json
import time
import pandas as pd
import os
from datetime import datetime
from css import container, center, set_video_background, autorisation
import plotly.express as px


WAREHOUSE_FILE = "warehouse.csv"
ORDERS_HISTORY_FILE = "orders_history.csv"
st.set_page_config(page_title="Control Panel", layout='wide')

if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'products' not in st.session_state:
    st.session_state.products = [{'product_id': 1, 'quantity': 1}]
if 'warehouse_logs' not in st.session_state:
    st.session_state.warehouse_logs = []
if 'warehouse_log_container' not in st.session_state:
    st.session_state.warehouse_log_container = None
if 'log_container' not in st.session_state:
    st.session_state.log_container = None

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    set_video_background("video.mp4")
    container()
    center()
    st.markdown('<h1 class="centered">Welcome!</h1>', unsafe_allow_html=True)
    st.markdown('''<h5 class="centered">
    This is a web control panel for company managers.<br>
    To access sales analytics, order management and delivery system, please log in
    </h5>''', unsafe_allow_html=True)

    autorisation()
    col1, col2, col3 = st.columns([1, 5, 1])
    with col2:
        with st.form("auth_form"):
            username = st.text_input("Username")
            password = st.text_input("Password")
            btn_container = st.container()
        with btn_container:
            cols = st.columns([3, 1, 3])
            with cols[1]:
                submit_button = st.form_submit_button("Sign in")

        if submit_button:
            with open('users.json', 'r') as f:
                users = json.load(f)
            if username in users and users[username] == password:
                st.session_state.authenticated = True
                st.success("Авторизация успешна!")
                st.rerun()
            else:
                st.error("Неверные учетные данные")
    st.stop()


def load_warehouse_data():
    if not os.path.exists(WAREHOUSE_FILE):
        initial_data = [
            {"product_id": 101, "name": "Ноутбук", "quantity": 15, "price": 50000},
            {"product_id": 102, "name": "Смартфон", "quantity": 30, "price": 30000},
            {"product_id": 103, "name": "Наушники", "quantity": 50, "price": 5000}
        ]
        pd.DataFrame(initial_data).to_csv(WAREHOUSE_FILE, index=False)
        return initial_data
    return pd.read_csv(WAREHOUSE_FILE).to_dict('records')


def save_warehouse_data(data):
    pd.DataFrame(data).to_csv(WAREHOUSE_FILE, index=False)


def load_orders_history():
    if not os.path.exists(ORDERS_HISTORY_FILE):
        return pd.DataFrame(columns=[
            "order_id", "timestamp", "status", "products", "total_items",
            "total_price", "payment_method", "destination"
        ])
    return pd.read_csv(ORDERS_HISTORY_FILE)

if 'order_counter' not in st.session_state:
    history_df = load_orders_history()
    st.session_state.order_counter = history_df['order_id'].max() if not history_df.empty else 0

# Инициализация данных
if 'warehouse' not in st.session_state:
    st.session_state.warehouse = load_warehouse_data()


def update_warehouse_log_display():
    if st.session_state.warehouse_log_container is not None:
        with st.session_state.warehouse_log_container:
            st.markdown("""<div style="
                border: 1px solid #7D8481;
                border-radius: 10px;
                padding: 15px;
                height: 248px;
                overflow-y: auto;
                background-color: rgba(0, 0, 0, 0.5);
                margin-bottom: 15px;
                font-family: monospace;
                color: #eee;
            ">
                <div style="margin: 0; padding: 0;">
                    {logs_content}
                </div>
            </div>""".format(
                logs_content='\n'.join(
                    f'<div style="margin: 0; padding: 0; line-height: 1.5;">{log}</div>'
                    for log in st.session_state.warehouse_logs
                ) if st.session_state.warehouse_logs else 'No warehouse logs yet...'
            ), unsafe_allow_html=True)


def add_warehouse_log(message, color=None):
    timestamp = time.strftime("%H:%M:%S")

    colors = {
        "error": "red",
        "success": "green",
        "warning": "yellow",
        "default": "white"
    }

    color_code = colors.get(color, colors["default"])
    log_entry = f"[{timestamp}] {message}"

    colored_log = f'<span style="color:{color_code}">{log_entry}</span>'
    st.session_state.warehouse_logs.append(colored_log)

    if len(st.session_state.warehouse_logs) > 9:
        st.session_state.warehouse_logs.pop(0)

    update_warehouse_log_display()


def update_log_display():
    if st.session_state.log_container is not None:
        with st.session_state.log_container:
            st.markdown("""<div style="
                border: 1px solid #7D8481;
                border-radius: 10px;
                padding: 15px;
                height: 217px;
                overflow-y: auto;
                background-color: rgba(0, 0, 0, 0.5);
                margin-bottom: 15px;
                font-family: monospace;
                color: #eee;
            ">
                <div style="margin: 0; padding: 0;">
                    {logs_content}
                </div>
            </div>""".format(
                logs_content='\n'.join(
                    f'<div style="margin: 0; padding: 0; line-height: 1.5;">{log}</div>'
                    for log in st.session_state.logs
                ) if st.session_state.logs else 'No logs yet...'
            ), unsafe_allow_html=True)


def add_log(message, color=None):
    timestamp = time.strftime("%H:%M:%S")

    colors = {
        "error": "red",
        "default": "white"
    }

    color_code = colors.get(color, colors["default"])
    log_entry = f"[{timestamp}] {message}"

    colored_log = f'<span style="color:{color_code}">{log_entry}</span>'
    st.session_state.logs.append(colored_log)

    if len(st.session_state.logs) > 8:
        st.session_state.logs.pop(0)

    update_log_display()


def check_stock_availability(products):
    errors = []
    for product in products:
        product_id = product['product_id']
        quantity = product['quantity']

        product_in_warehouse = next(
            (item for item in st.session_state.warehouse if item['product_id'] == product_id),
            None
        )

        if not product_in_warehouse:
            errors.append(f"Товар с ID {product_id} отсутствует на складе")
        elif product_in_warehouse['quantity'] < quantity:
            available = product_in_warehouse['quantity']
            errors.append(f"Недостаточно товара ID {product_id}. Доступно: {available}, Заказано: {quantity}")

    return errors


def reserve_products(products):
    try:
        for product in products:
            product_id = product['product_id']
            quantity = product['quantity']

            for item in st.session_state.warehouse:
                if item['product_id'] == product_id:
                    if item['quantity'] >= quantity:
                        item['quantity'] -= quantity
                        add_log(f"Товар ID {product_id} зарезервирован: -{quantity}")
                    else:
                        raise ValueError(f"Недостаточно товара ID {product_id}")

        save_warehouse_data(st.session_state.warehouse)
        return True
    except Exception as e:
        add_log(f"Ошибка резервирования товаров: {str(e)}", "error")
        return False


def return_products_to_stock(products):
    try:
        for product in products:
            product_id = product['product_id']
            quantity = product['quantity']

            product_found = False
            for item in st.session_state.warehouse:
                if item['product_id'] == product_id:
                    item['quantity'] += quantity
                    product_found = True
                    add_log(f"Товар ID {product_id} возвращен на склад: +{quantity}")
                    break

            if not product_found:
                st.session_state.warehouse.append({
                    "product_id": product_id,
                    "name": f"Товар {product_id}",
                    "quantity": quantity,
                    "price": 0
                })
                add_log(f"Товар ID {product_id} добавлен на склад: +{quantity}")

        save_warehouse_data(st.session_state.warehouse)
        return True
    except Exception as e:
        add_log(f"Ошибка возврата товаров: {str(e)}", "error")
        return False


def calculate_order_total(products):
    total_price = 0
    total_items = 0

    for product in products:
        product_id = product['product_id']
        quantity = product['quantity']
        total_items += quantity

        product_in_warehouse = next(
            (item for item in st.session_state.warehouse if item['product_id'] == product_id),
            None
        )

        if product_in_warehouse:
            total_price += product_in_warehouse['price'] * quantity

    return total_items, total_price


def process_payment():
    add_log("Начало обработки платежа...")
    time.sleep(0.2)
    progress_bar = st.progress(0)

    for percent in range(0, 101, 10):
        time.sleep(0.3)
        progress_bar.progress(percent)
        if percent < 30:
            payment_status.info(f"Проверка платежных данных... {percent}%")
        elif percent < 70:
            payment_status.info(f"Связь с банком... {percent}%")
        else:
            payment_status.info(f"Завершение транзакции... {percent}%")

    progress_bar.empty()
    add_log("Платеж успешно обработан")


if 'order_counter' not in st.session_state:
    st.session_state.order_counter = 0


def place_order(products, payment_method, destination):
    stock_errors = check_stock_availability(products)
    if stock_errors:
        for error in stock_errors:
            add_log(error, "error")
        payment_status.error("Ошибка: недостаточно товаров на складе")
        return False

    if not reserve_products(products):
        payment_status.error("Ошибка резервирования товаров")
        return False

    total_items, total_price = calculate_order_total(products)

    process_payment()

    st.session_state.order_counter += 1
    order_id = st.session_state.order_counter
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    order_data = {
        "order_id": order_id,
        "timestamp": timestamp,
        "status": "завершен",
        "products": json.dumps(products),
        "total_items": total_items,
        "total_price": total_price,
        "payment_method": payment_method,
        "destination": destination
    }

    try:
        history_df = load_orders_history()
        history_df = history_df[history_df['order_id'] != order_id]
        new_order_df = pd.DataFrame([order_data])
        history_df = pd.concat([history_df, new_order_df], ignore_index=True)
        history_df.to_csv(ORDERS_HISTORY_FILE, index=False)

        add_log(f"Заказ успешно оформлен! ID: {order_id}")
        st.session_state.products = [{'product_id': 1, 'quantity': 1}]
        return True
    except Exception as e:
        add_log(f"Ошибка сохранения заказа: {str(e)}", "error")
        return False


def cancel_last_order():
    try:
        history_df = load_orders_history()

        last_completed = history_df[history_df['status'] == 'завершен'].sort_values('timestamp', ascending=False)

        if last_completed.empty:
            add_log("Нет завершенных заказов для отмены", "error")
            return False

        last_order = last_completed.iloc[0]
        order_id = last_order['order_id']

        canceled_order = {
            "order_id": order_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "отмененный",
            "products": last_order['products'],
            "total_items": last_order['total_items'],
            "total_price": 0,
            "payment_method": "N/A",
            "destination": "N/A"
        }

        products = json.loads(last_order['products'])
        if not return_products_to_stock(products):
            add_log("Ошибка при возврате товаров", "error")
            return False

        # Обновляем историю - удаляем старую запись, добавляем новую
        history_df = history_df[history_df['order_id'] != order_id]
        new_order_df = pd.DataFrame([canceled_order])
        history_df = pd.concat([history_df, new_order_df], ignore_index=True)
        history_df.to_csv(ORDERS_HISTORY_FILE, index=False)

        add_log(f"Заказ отменен. ID: {order_id}")
        return True

    except Exception as e:
        add_log(f"Ошибка при отмене заказа: {str(e)}", "error")
        return False


def add_product():
    st.session_state.products.append({'product_id': 1, 'quantity': 1})


def remove_product():
    if len(st.session_state.products) > 1:
        st.session_state.products.pop()
        add_log("Товар удален из заказа")
    else:
        add_log("Нельзя удалить последний товар")

container()
set_video_background("video.mp4")
autorisation()

selected = option_menu(
    menu_title=None,
    options=["Order Form", "Analytics", "Warehouse"],
    icons=["cart", "bar-chart", "box-seam"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "3px !important", "background-color": "#000"},
        "icon": {"color": "#eee", "font-size": "14px"},
        "nav-link": {
            "font-size": "16px",
            "text-align": "center",
            "margin": "0px",
            "--hover-color": "#eee",
            "color": "#eee",
            "font-weight": "bold"
        },
        "nav-link-selected": {"background-color": "#7D8481"},
    }
)

if selected == "Order Form":
    st.write('')

    col1, col2, col3, col4 = st.columns([0.6, 0.6, 4.8, 6])
    with col1:
        if st.button("➕", key="add_product"):
            add_product()
            st.rerun()
    with col2:
        if st.button("➖", key="remove_product"):
            remove_product()
            st.rerun()
    with col4:
        pass

    with st.form("order_form"):
        col1, col2 = st.columns(2)
        with col1:
            for i, product in enumerate(st.session_state.products):
                cols = st.columns(2)
                with cols[0]:
                    product_id = st.number_input(
                        f"Product ID #{i + 1}",
                        min_value=1,
                        step=1,
                        value=product['product_id'],
                        key=f"product_id_{i}"
                    )
                with cols[1]:
                    quantity = st.number_input(
                        "Quantity",
                        min_value=1,
                        step=1,
                        value=product['quantity'],
                        key=f"quantity_{i}"
                    )

                st.session_state.products[i] = {'product_id': product_id, 'quantity': quantity}

            st.write("")
            payment_method = st.selectbox("Payment Method", ["Карта", "Наличные", "СБП"])
            destination = st.selectbox("Destination", ["Казань", "Другой город"])

            st.write("")
            c1, c2, c3 = st.columns([1.29, 1.4, 1.38])
            with c1:
                submit_order = st.form_submit_button("Place New Order")
            with c2:
                calculate_shipping = st.form_submit_button("Calculate Shipping")
            with c3:
                cancel_order = st.form_submit_button("Cancel Last Order")

        with col2:
            with st.container():
                st.write('')
                st.write('')
                if st.session_state.log_container is None:
                    st.session_state.log_container = st.empty()
                update_log_display()

            payment_status = st.empty()

            if submit_order:
                success = place_order(st.session_state.products, payment_method, destination)
                if success:
                    st.session_state.products = [{'product_id': 1, 'quantity': 1}]
                    payment_status.success('Заказ успешно оформлен')

            if calculate_shipping:
                with st.spinner("Calculating shipping..."):
                    add_log("Shipping calculation completed")
                    payment_status.warning(f"Shipping cost: {'Free' if destination == 'Казань' else '500 руб.'}")

            if cancel_order:
                if cancel_last_order():
                    payment_status.warning("Последний заказ отменен")
                else:
                    payment_status.error("Ошибка при отмене заказа")

elif selected == "Warehouse":

    st.write('')

    if 'warehouse' not in st.session_state:
        st.session_state.warehouse = load_warehouse_data()

    col1, col2, clo3 = st.columns(3)

    with col1:
        with st.form("add_form", clear_on_submit=True):
            c = st.columns(2)
            with c[0]:
                product_id = st.number_input("ID товара", min_value=1, step=1, key="add_id")
            with c[1]:
                quantity = st.number_input("Количество", min_value=1, step=1, value=1, key="add_qty")
            price = st.number_input("Цена (₽)", min_value=0, step=100, key="add_price")

            if st.form_submit_button("Добавить"):
                try:
                    product_exists = False
                    for product in st.session_state.warehouse:
                        if product['product_id'] == product_id:
                            product['quantity'] += quantity
                            add_warehouse_log(f"ID {product_id}: +{quantity}")

                            if price > 0:
                                product['price'] = price
                                add_warehouse_log(f"Обновлена цена товара ID {product_id}: {price}₽")

                            product_exists = True
                            break

                    if not product_exists:
                        if price <= 0:
                            st.error("Для нового товара укажите цену!")
                            add_warehouse_log(f"Ошибка добавления: не указана цена для ID {product_id}", "error")
                        else:
                            st.session_state.warehouse.append({
                                "product_id": product_id,
                                "name": f"Товар {product_id}",
                                "quantity": quantity,
                                "price": price
                            })
                            st.success(f"Добавлен новый товар ID {product_id}")
                            add_warehouse_log(f"Добавлен новый товар ID {product_id}", "success")

                    save_warehouse_data(st.session_state.warehouse)
                    st.rerun()
                except Exception as e:
                    st.error(f"Ошибка: {str(e)}")
                    add_warehouse_log(f"Ошибка при добавлении товара: {str(e)}", "error")

    with col2:
        with st.form("remove_form", clear_on_submit=True):
            product_id = st.number_input("ID товара", min_value=1, step=1, key="remove_id")
            quantity = st.number_input("Количество", min_value=1, step=1, value=1, key="remove_qty")

            if st.form_submit_button("Списать"):
                try:
                    product_found = False
                    for product in st.session_state.warehouse:
                        if product['product_id'] == product_id:
                            product_found = True
                            if product['quantity'] >= quantity:
                                product['quantity'] -= quantity
                                add_warehouse_log(f"ID {product_id}: -{quantity}", "warning")
                                if product['quantity'] <= 0:
                                    st.session_state.warehouse.remove(product)
                                    st.success("Товар полностью списан")
                                    add_warehouse_log(f"ID {product_id} полностью списан", "warning")
                            else:
                                st.error(f"Недостаточно товара! Доступно: {product['quantity']}")
                                add_warehouse_log(f"Недостаточно ID {product_id}", "error")
                            break

                    if not product_found:
                        st.error("Товар не найден")
                        add_warehouse_log(f"Ошибка: ID {product_id} не найден", "error")

                    save_warehouse_data(st.session_state.warehouse)
                    st.rerun()
                except Exception as e:
                    st.error(f"Ошибка: {str(e)}")
                    add_warehouse_log(f"Ошибка при списании товара: {str(e)}", "error")

    with clo3:
        if st.session_state.warehouse_log_container is None:
            st.session_state.warehouse_log_container = st.empty()
        update_warehouse_log_display()

    st.subheader("Текущие запасы")
    if st.session_state.warehouse:
        df = pd.DataFrame(st.session_state.warehouse)[["product_id", "quantity", "price"]]
        df.columns = ["ID", "Количество", "Цена (₽)"]

        st.data_editor(
            df,
            column_config={
                "ID": st.column_config.NumberColumn(width="small"),
                "Количество": st.column_config.NumberColumn(width="small"),
                "Цена (₽)": st.column_config.NumberColumn(width="small", format="%d")
            },
            hide_index=True,
            use_container_width=True,
            key="warehouse_table"
        )
    else:
        st.warning("Склад пуст")
        add_warehouse_log("Склад пуст", "warning")


elif selected == "Analytics":
    orders_df = load_orders_history()

    orders_df['date'] = pd.to_datetime(orders_df['timestamp']).dt.date
    orders_df['datetime'] = pd.to_datetime(orders_df['timestamp'])


    all_products = set()
    for products_json in orders_df['products']:
        products = json.loads(products_json)
        for product in products:
            all_products.add(product['product_id'])
    all_products = sorted(all_products)


    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            min_date = orders_df['date'].min()
            max_date = orders_df['date'].max()
            date_range = st.date_input(
                '', label_visibility="hidden",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )

        with col2:
            selected_products = st.multiselect(
                '', label_visibility="hidden",
                options=all_products,
                default=None,
                placeholder="Выберите ID продуктов...",
                format_func=lambda x: f"Выбрано {len(all_products)} продуктов" if x == all_products else str(x)
            )

    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = orders_df[
            (pd.to_datetime(orders_df['timestamp']).dt.date >= start_date) &
            (pd.to_datetime(orders_df['timestamp']).dt.date <= end_date)
            ]
    else:
        filtered_df = orders_df.copy()

    if not selected_products:
        pass
    else:
        product_filtered = []
        for idx, row in filtered_df.iterrows():
            products = json.loads(row['products'])
            if any(p['product_id'] in selected_products for p in products):
                product_filtered.append(True)
            else:
                product_filtered.append(False)
        filtered_df = filtered_df[product_filtered]

    tab1, tab2 = st.tabs(["Статистика заказов", "Ежедневные продажи"])

    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            status_counts = filtered_df['status'].value_counts().reset_index()
            status_counts.columns = ['status', 'count']

            fig = px.pie(
                status_counts,
                values='count',
                names='status',
                color='status',
                color_discrete_map={
                    'завершен': '#402a5e',
                    'отмененный': '#290838'
                },
                labels={'status': ''}
            )

            fig.update_traces(
                textposition='none',
                hole=0.3,
                marker=dict(line=dict(color='#000000', width=1.4)))

            fig.update_layout(
                xaxis_tickformat='%d %b %Y',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=380,
                margin=dict(l=20, r=20, t=40, b=20),
                legend=dict(
                    font=dict(size=16, color='white'),
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=1.04,
                ),
            )

            config = {'displayModeBar': False}
            st.plotly_chart(fig, use_container_width=True, config=config)

        with col2:
            for i in range(3):
                st.write('')
            # Кнопка для скачивания CSV
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Скачать историю заказов (CSV)",
                data=csv,
                file_name=f"orders_history_{start_date}_{end_date}.csv",
                mime='text/csv',
                use_container_width=True
            )

            # Статистика заказов
            stats_data = {
                "Показатель": [
                    "Всего заказов",
                    "Завершенные заказы",
                    "Отмененные заказы",
                    "Процент завершенных",
                    "Процент отмененных"
                ],
                "Значение": [
                    len(filtered_df),
                    len(filtered_df[filtered_df['status'] == 'завершен']),
                    len(filtered_df[filtered_df['status'] == 'отмененный']),
                    f"{len(filtered_df[filtered_df['status'] == 'завершен']) / len(filtered_df) * 100:.1f}%" if len(
                        filtered_df) > 0 else '0%',
                    f"{len(filtered_df[filtered_df['status'] == 'отмененный']) / len(filtered_df) * 100:.1f}%" if len(
                        filtered_df) > 0 else '0%'
                ]
            }

            st.dataframe(
                pd.DataFrame(stats_data),
                column_config={
                    "Показатель": st.column_config.TextColumn(width="medium"),
                    "Значение": st.column_config.TextColumn(width="small")
                },
                hide_index=True,
                use_container_width=True
            )

    with tab2:
        if len(filtered_df) > 0:
            # Группируем по дате и статусу (только завершенные заказы)
            daily_sales = filtered_df[filtered_df['status'] == 'завершен'].groupby('date')[
                'total_price'].sum().reset_index()

            # Создаем график
            fig = px.bar(
                daily_sales,
                x='date',
                y='total_price',
                labels={'date': '', 'total_price': ''},
                color_discrete_sequence=['#4B0082']
            )

            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False, color='white'),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', color='white'),
                font=dict(color='white'),
                margin=dict(l=20, r=20, t=30, b=20)
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Нет данных для отображения по выбранным фильтрам")

