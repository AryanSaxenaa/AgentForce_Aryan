// Sample JavaScript code with a few functions to demonstrate test generation.

function add(a, b) {
  return a + b;
}

function divide(a, b) {
  if (b === 0) throw new Error("Division by zero");
  return a / b;
}

function findMax(arr) {
  if (!Array.isArray(arr) || arr.length === 0) return null;
  return arr.reduce((m, x) => (x > m ? x : m), arr[0]);
}

function fibonacci(n) {
  if (n < 0) throw new Error("Negative not allowed");
  if (n === 0) return 0;
  if (n === 1) return 1;
  let a = 0, b = 1;
  for (let i = 2; i <= n; i++) {
    const t = a + b;
    a = b;
    b = t;
  }
  return b;
}

module.exports = { add, divide, findMax, fibonacci };
