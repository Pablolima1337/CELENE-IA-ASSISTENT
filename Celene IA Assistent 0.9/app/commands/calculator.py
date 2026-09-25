import ast
import operator


class Calculator:
    OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    def calculate(self, expression: str):
        try:
            tree = ast.parse(
                expression,
                mode="eval"
            )

            result = self._evaluate(tree.body)

            return result

        except Exception as error:
            print(
                f"[CALCULATOR] Erro: {error}"
            )

            return None

    def _evaluate(self, node):
        if isinstance(node, ast.Constant):
            if isinstance(
                node.value,
                (int, float)
            ):
                return node.value

            raise ValueError(
                "Valor inválido."
            )

        if isinstance(node, ast.BinOp):
            operator_type = type(node.op)

            if operator_type not in self.OPERATORS:
                raise ValueError(
                    "Operação não permitida."
                )

            left = self._evaluate(
                node.left
            )

            right = self._evaluate(
                node.right
            )

            return self.OPERATORS[
                operator_type
            ](
                left,
                right
            )

        if isinstance(node, ast.UnaryOp):
            operator_type = type(node.op)

            if operator_type not in self.OPERATORS:
                raise ValueError(
                    "Operação não permitida."
                )

            value = self._evaluate(
                node.operand
            )

            return self.OPERATORS[
                operator_type
            ](
                value
            )

        raise ValueError(
            "Expressão inválida."
        )