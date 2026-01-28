from decimal import Decimal, ROUND_HALF_UP


class FinanceCalculator:
    # Custo fixo do AbacatePay por transação
    GATEWAY_FIXED_FEE = Decimal('0.80')

    @classmethod
    def calculate_fees(cls, amount):
        """
        Calcula o split financeiro com proteção contra prejuízo.
        """
        amount = Decimal(str(amount))

        # Validação de segurança mínima
        if amount < cls.GATEWAY_FIXED_FEE:
            raise ValueError(f"O valor mínimo do pedido deve ser R$ {cls.GATEWAY_FIXED_FEE}")

        # --- REGRA DE PROTEÇÃO (< R$ 20) ---
        if amount < Decimal('20.00'):
            # Lykos não lucra nada, apenas repassa o custo do gateway
            platform_gross_income = cls.GATEWAY_FIXED_FEE
            platform_pct = Decimal('0.00')
            lykos_real_profit = Decimal('0.00')

        # --- REGRA PADRÃO (>= R$ 20) ---
        else:
            if amount <= 100:
                platform_pct = Decimal('0.04')  # 4%
            elif amount <= 400:
                platform_pct = Decimal('0.06')  # 6%
            elif amount <= 700:
                platform_pct = Decimal('0.08')  # 8%
            else:
                platform_pct = Decimal('0.10')  # 10%

            # Calcula retenção bruta
            platform_gross_income = (amount * platform_pct).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            # Lucro real = O que retivemos - O que pagaremos ao Abacate
            lykos_real_profit = platform_gross_income - cls.GATEWAY_FIXED_FEE

        # O Freelancer recebe o que sobrar (Total - Retenção Bruta)
        freelancer_net_income = amount - platform_gross_income

        return {
            "amount": amount,
            "platform_pct": platform_pct,
            "platform_fee": platform_gross_income,  # Valor total retido do pedido
            "freelancer_net": freelancer_net_income,
            "gateway_cost": cls.GATEWAY_FIXED_FEE,
            "lykos_profit": lykos_real_profit
        }