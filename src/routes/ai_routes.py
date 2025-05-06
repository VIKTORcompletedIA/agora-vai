# src/routes/ai_routes.py

from flask import Blueprint, request, jsonify
from src.services.ai_service import ai_service

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/train', methods=['POST'])
def train_ai():
    """Inicia o treinamento da IA para um ativo específico."""
    data = request.json
    
    # Validar dados
    if not data or 'symbol' not in data:
        return jsonify({"status": "error", "message": "Símbolo do ativo é obrigatório."}), 400
    
    # Extrair parâmetros
    symbol = data.get('symbol')
    region = data.get('region', 'US')
    episodes = int(data.get('episodes', 100))
    initial_balance = float(data.get('initial_balance', 10000))
    trade_amount = float(data.get('trade_amount', 1000))
    target_profit_abs = float(data.get('target_profit_abs', 330))
    stop_loss_abs = float(data.get('stop_loss_abs', 600))
    
    # Iniciar treinamento
    result = ai_service.start_training(
        symbol=symbol,
        region=region,
        episodes=episodes,
        initial_balance=initial_balance,
        trade_amount=trade_amount,
        target_profit_abs=target_profit_abs,
        stop_loss_abs=stop_loss_abs
    )
    
    return jsonify(result)

@ai_bp.route('/status', methods=['GET'])
def get_training_status():
    """Verifica o status do treinamento da IA para um ativo específico."""
    symbol = request.args.get('symbol')
    region = request.args.get('region', 'US')
    
    if not symbol:
        return jsonify({"status": "error", "message": "Símbolo do ativo é obrigatório."}), 400
    
    status = ai_service.get_training_status(symbol, region)
    return jsonify(status)

@ai_bp.route('/simulate', methods=['POST'])
def run_simulation():
    """Executa uma simulação com a IA treinada."""
    data = request.json
    
    # Validar dados
    if not data or 'symbol' not in data:
        return jsonify({"status": "error", "message": "Símbolo do ativo é obrigatório."}), 400
    
    # Extrair parâmetros
    symbol = data.get('symbol')
    region = data.get('region', 'US')
    trade_amount = float(data.get('trade_amount', 1000))
    target_profit_abs = float(data.get('target_profit_abs', 330))
    stop_loss_abs = float(data.get('stop_loss_abs', 600))
    
    # Executar simulação
    result = ai_service.run_simulation(
        symbol=symbol,
        region=region,
        trade_amount=trade_amount,
        target_profit_abs=target_profit_abs,
        stop_loss_abs=stop_loss_abs
    )
    
    return jsonify(result)

@ai_bp.route('/models', methods=['GET'])
def get_available_models():
    """Obtém a lista de modelos disponíveis."""
    models = ai_service.get_available_models()
    return jsonify({"status": "success", "models": models})
