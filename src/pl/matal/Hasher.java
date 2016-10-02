package pl.matal;

/**
 * Created by aleksander on 26.09.16.
 */
public class Hasher {
    private static final int BASE = 257;

    public int setServerNumber(Request request, int serverCount) {
        int hash = 0;
        for (char c : request.getKey().toCharArray()) {
            hash = hash * BASE + (int) c;
        }

        long interval = (long) Integer.MAX_VALUE - (long) Integer.MIN_VALUE;
        long hashAbsolute = (long) hash - (long) Integer.MIN_VALUE;

        int number = (int) (hashAbsolute * (long) serverCount / interval);
        // In an unlikely event that hash will equal to MAX_VALUE, we have to
        // handle assigning number manually.
        if (number == serverCount) {
            number = serverCount - 1;
        }
        // TODO: is that still necessary?
        request.setServerNumber(number);
        return number;
    }
}
