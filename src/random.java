import java.util.Random;
public class random {
    public static void main(String[] args) {
        Random rand = new Random();
        String letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
        String word = "";

        for (int i = 0; i < 5; i++) {
           int n = rand.nextInt(5);
            word += letters.charAt(n);
        }
        System.out.println(word);
    }
}