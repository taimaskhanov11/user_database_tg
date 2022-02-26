






def register_handlers_subscriptions(dp: Dispatcher):
    dp.register_callback_query_handler(subscribe, text_startswith="subscribe_")
    dp.register_callback_query_handler(reject_payment, text="reject_payment")
    # dp.register_callback_query_handler(subscribe_month, text="subscribe_month")