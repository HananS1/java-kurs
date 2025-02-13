import java.util.Scanner;
public class While {
    public static void main(String[] args) {
        Scanner scan = new Scanner(System.in);
        int zahl = 3;
        while (zahl == 3) {
            System.out.println("All i need is a while");
            System.out.println("Hello");
            System.out.println("Wollen Sie noch einmal? (3 = ja, 0 = nein)");
            zahl = scan.nextInt();
        }
    }
}
