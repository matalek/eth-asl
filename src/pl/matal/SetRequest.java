package pl.matal;

import java.nio.channels.SocketChannel;
import java.util.Arrays;

/**
 * Created by aleksander on 26.09.16.
 */
public class SetRequest extends Request {
    private int[] params;
    private String value;
    private boolean isDelete;

    public SetRequest(SocketChannel channel, String key, int[] params, String value, boolean toLog, boolean isDelete) {
        super(channel, key, toLog);
        this.params = params;
        this.value = value;
        this.isDelete = isDelete;
    }

    public int[] getParams() {
        return params;
    }

    public String getValue() {
        return value;
    }

    public boolean isDelete() {
        return isDelete;
    }

    @Override
    public int getType() {
        return TYPE_SET;
    }
}
