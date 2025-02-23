public class Arrays {
    public static void main(String[] args) {

        int[] numbers =  new int[1000];//Array mit 1000 Elementen

        for (int i = 0; i < numbers.length; i++) {
            numbers[i] = i + 1;
        }
        for (int i = 0; i < numbers.length; i++) {
            System.out.println(numbers[i]);
        }
    }

}
