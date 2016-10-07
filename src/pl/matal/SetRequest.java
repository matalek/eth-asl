package pl.matal;

import java.nio.channels.SocketChannel;
import java.util.Arrays;

/**
 * Created by aleksander on 26.09.16.
 */
public class SetRequest extends Request {
    private int[] params;
    private String value;

    public SetRequest(SocketChannel channel, String key, int[] params, String value, boolean toLog) {
        super(channel, key, toLog);
        this.params = params;
        this.value = value;
    }

    public int[] getParams() {
        return params;
    }

    public String getValue() {
        return value;
    }

    @Override
    public int getType() {
        return TYPE_SET;
    }

    @Override
    public String toString() {
        return "SetRequest{" +
                "key='" + key + '\'' +
                "params=" + Arrays.toString(params) +
                '}';
    }


}
