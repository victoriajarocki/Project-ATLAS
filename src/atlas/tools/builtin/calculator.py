"""Safe arithmetic calculator tool for Project ATLAS."""

import ast
import operator
from collections.abc import Callable
from typing import Any

from atlas.tools.base import (
    Tool,
    ToolDefinition,
    ToolResult,
    ToolRiskLevel,
    ToolValidationError,
)

Number = int | float
BinaryOperation = Callable[[Number, Number], Number]
UnaryOperation = Callable[[Number], Number]


_BINARY_OPERATIONS: dict[type[ast.operator], BinaryOperation] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

_UNARY_OPERATIONS: dict[type[ast.unaryop], UnaryOperation] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


class CalculatorTool(Tool):
    """Evaluate safe arithmetic expressions."""

    MAX_EXPRESSION_LENGTH = 200
    MAX_POWER_EXPONENT = 100

    @property
    def definition(self) -> ToolDefinition:
        """Return the calculator definition."""
        return ToolDefinition(
            name="calculator",
            description=(
                "Evaluate a basic arithmetic expression using "
                "addition, subtraction, multiplication, division, "
                "remainders, powers, and parentheses."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": ("Arithmetic expression to evaluate."),
                    }
                },
                "required": ["expression"],
                "additionalProperties": False,
            },
            risk_level=ToolRiskLevel.LOW,
            requires_confirmation=False,
        )

    def execute(
        self,
        arguments: dict[str, Any],
    ) -> ToolResult:
        """Evaluate the requested arithmetic expression."""
        expression_value = arguments.get("expression")

        if not isinstance(expression_value, str):
            raise ToolValidationError("The calculator requires a string named 'expression'.")

        expression = expression_value.strip()

        if not expression:
            raise ToolValidationError("The calculator expression cannot be empty.")

        if len(expression) > self.MAX_EXPRESSION_LENGTH:
            raise ToolValidationError("The calculator expression is too long.")

        try:
            syntax_tree = ast.parse(
                expression,
                mode="eval",
            )
            value = self._evaluate_node(syntax_tree.body)
        except (
            SyntaxError,
            TypeError,
            ValueError,
            ZeroDivisionError,
            OverflowError,
        ) as error:
            raise ToolValidationError(f"Invalid calculator expression: {error}") from error

        return ToolResult(
            tool_name=self.definition.name,
            success=True,
            output=str(value),
        )

    def _evaluate_node(self, node: ast.AST) -> Number:
        """Recursively evaluate an approved syntax node."""
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool):
                raise ToolValidationError("Boolean values are not supported.")

            if isinstance(node.value, (int, float)):
                return node.value

            raise ToolValidationError("Only numeric constants are supported.")

        if isinstance(node, ast.BinOp):
            binary_operation_type = type(node.op)

            if binary_operation_type not in _BINARY_OPERATIONS:
                raise ToolValidationError("That arithmetic operation is not supported.")

            left = self._evaluate_node(node.left)
            right = self._evaluate_node(node.right)

            if isinstance(node.op, ast.Pow) and abs(right) > self.MAX_POWER_EXPONENT:
                raise ToolValidationError("The requested exponent is too large.")

            binary_operation = _BINARY_OPERATIONS[binary_operation_type]

            return binary_operation(left, right)

        if isinstance(node, ast.UnaryOp):
            unary_operation_type = type(node.op)

            if unary_operation_type not in _UNARY_OPERATIONS:
                raise ToolValidationError("That unary operation is not supported.")

            operand = self._evaluate_node(node.operand)

            unary_operation = _UNARY_OPERATIONS[unary_operation_type]

            return unary_operation(operand)

        raise ToolValidationError("The expression contains unsupported syntax.")
