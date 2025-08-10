// Sample Java code for demonstrating test generation.

public class Sample {
    public static int add(int a, int b) {
        return a + b;
    }

    public static int divide(int a, int b) {
        if (b == 0) throw new IllegalArgumentException("Division by zero");
        return a / b;
    }

    public static Integer findMax(Integer[] arr) {
        if (arr == null || arr.length == 0) return null;
        int max = arr[0];
        for (int i = 1; i < arr.length; i++) {
            if (arr[i] > max) max = arr[i];
        }
        return max;
    }

    public static long fibonacci(int n) {
        if (n < 0) throw new IllegalArgumentException("Negative not allowed");
        if (n == 0) return 0;
        if (n == 1) return 1;
        long a = 0, b = 1;
        for (int i = 2; i <= n; i++) {
            long t = a + b;
            a = b;
            b = t;
        }
        return b;
    }
}
