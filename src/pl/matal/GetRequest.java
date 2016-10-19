package pl.matal;

import java.nio.channels.SocketChannel;

/**
 * Created by aleksander on 26.09.16.
 *
 * Class representing get requests.
 */
public class GetRequest extends Request {
    public GetRequest(SocketChannel channel, String key, boolean toLog) {
        super(channel, key, toLog);
    }

    @Override
    public int getType() {
        return TYPE_GET;
    }
}
