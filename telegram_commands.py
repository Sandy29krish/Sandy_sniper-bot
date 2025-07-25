from flask import Flask, request

app = Flask(__name__)

@app.route('/telegram_webhook', methods=['POST'])
def telegram_webhook():
    update = request.get_json()
    # Here you process incoming Telegram updates/commands
    print(f"Received update: {update}")
    return 'OK'

def start_telegram_command_server():
    print("Starting Telegram command server...")
    app.run(host='0.0.0.0', port=5000)

def get_swing_bot_status():
    # This can be improved to reflect real bot status
    return True



def handle_close_position(kite, telegram_id):
    # Check current open positions
    positions = kite.positions()['net']
    swing_positions = [p for p in positions if p['product'] == 'NRML' and p['quantity'] != 0]

    if not swing_positions:
        send_telegram_message("ℹ️ No open swing position to close.", telegram_id)
        return

    for pos in swing_positions:
        try:
            kite.place_order(
                variety=kite.VARIETY_REGULAR,
                exchange=pos['exchange'],
                tradingsymbol=pos['tradingsymbol'],
                transaction_type='SELL' if pos['quantity'] > 0 else 'BUY',
                quantity=abs(pos['quantity']),
                order_type=kite.ORDER_TYPE_MARKET,
                product=pos['product']
            )
            send_telegram_message(f"🛑 Emergency Exit Triggered: Closed position in {pos['tradingsymbol']}", telegram_id)
        except Exception as e:
            send_telegram_message(f"❌ Failed to close position in {pos['tradingsymbol']}: {str(e)}", telegram_id)
