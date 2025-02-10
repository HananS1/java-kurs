import java.util.Scanner;
public class scanner {
    public static void main(String[] args) {
        Scanner zahl = new Scanner(System.in);
        int z;
        String Wort;
        System.out.println("hey bitte gib dein Alter ein:");

        z = zahl.nextInt();

        System.out.println("Dein Alter ist ist in Deutschland " + (z +2));

        Scanner wort = new Scanner(System.in);

        System.out.println("Wie ist dein Name: ");

        Wort = wort.nextLine();

        System.out.println("Dein Name ist: " + Wort);

    }
}
