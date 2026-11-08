const FUNCTION_TYPES = new Set(['FunctionDeclaration', 'FunctionExpression', 'ArrowFunctionExpression'])
const SKIP_KEYS = new Set(['parent', 'loc', 'range', 'tokens', 'comments', 'leadingComments', 'trailingComments'])

const childNodes = (node) =>
  Object.keys(node)
    .filter((key) => !SKIP_KEYS.has(key))
    .flatMap((key) => [node[key]].flat())
    .filter((value) => value !== null && typeof value === 'object' && typeof value.type === 'string')

const returnsInside = (node) =>
  childNodes(node).flatMap((child) => (FUNCTION_TYPES.has(child.type) ? [] : returnsOf(child)))

const returnsOf = (node) => (node.type === 'ReturnStatement' ? [node] : returnsInside(node))

const isExpressionArrow = (node) =>
  node.type === 'ArrowFunctionExpression' && node.body.type !== 'BlockStatement'

const describe = (count) => `в функции ${count} return, разрешён только один — последним оператором`

const inspect = (context, node) => {
  const statements = node.body.body
  const found = returnsInside(node.body)
  const last = statements[statements.length - 1]
  const single = found.length === 1 && found[0] === last
  return found.length <= 1 && (found.length === 0 || single) ? undefined : report(context, node, found, last)
}

const report = (context, node, found, last) => {
  const tail = found.length === 1 && last !== found[0] ? 'return должен быть последним оператором функции' : describe(found.length)
  return context.report({ node, message: tail, loc: node.loc.start })
}

const guard = (context, node) => (isExpressionArrow(node) ? undefined : inspect(context, node))

export default {
  meta: {
    type: 'suggestion',
    docs: { description: 'Ровно один return, и он последний оператор функции' },
    schema: [],
    messages: {},
  },
  create: (context) => ({
    'FunctionDeclaration, FunctionExpression, ArrowFunctionExpression': (node) => guard(context, node),
  }),
}
