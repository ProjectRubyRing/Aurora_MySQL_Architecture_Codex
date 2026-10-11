import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Properties;

/** Connection example, not a production job runner. No automatic transaction retry. */
public final class BatchConnectionExample {
    private BatchConnectionExample() {}

    private static String required(String name) {
        String value = System.getenv(name);
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException("Missing configuration: " + name);
        }
        return value;
    }

    public static Connection connect() throws SQLException, IOException, ClassNotFoundException {
        String region = required("AWS_REGION");
        if (!region.equals("ap-northeast-1") && !region.equals("ap-northeast-3")) {
            throw new IllegalArgumentException("Unexpected deployment region");
        }
        String host = required("DB_PROXY_HOST");
        if (!host.matches("[a-zA-Z0-9.-]+") || !host.contains(".proxy-")
                || !host.endsWith("." + region + ".rds.amazonaws.com")) {
            throw new IllegalArgumentException("Invalid regional default Proxy endpoint");
        }
        String database = required("DB_NAME");
        if (!database.matches("[a-zA-Z][a-zA-Z0-9_]*")) {
            throw new IllegalArgumentException("Invalid database name");
        }
        Properties settings = new Properties();
        settings.setProperty("user", required("DB_USER"));
        // Secret provider writes the exact password, without an added newline, to a protected file.
        settings.setProperty("password", Files.readString(Path.of(required("DB_PASSWORD_FILE"))));
        settings.setProperty("sslMode", "VERIFY_IDENTITY");
        settings.setProperty("tlsVersions", "TLSv1.2,TLSv1.3");
        settings.setProperty("connectTimeout", "5000");
        settings.setProperty("socketTimeout", "150000");
        settings.setProperty("characterEncoding", "UTF-8");
        settings.setProperty("connectionTimeZone", "UTC");
        settings.setProperty("forceConnectionTimeZoneToSession", "false");
        settings.setProperty("allowPublicKeyRetrieval", "false");
        settings.setProperty("autoReconnect", "false");
        settings.setProperty("allowMultiQueries", "false");
        settings.setProperty("allowLoadLocalInfile", "false");
        settings.setProperty("useServerPrepStmts", "false");
        settings.setProperty("continueBatchOnError", "false");
        settings.setProperty("queryTimeoutKillsConnection", "true");
        Class.forName("com.mysql.cj.jdbc.Driver");
        return DriverManager.getConnection("jdbc:mysql://" + host + ":3306/" + database, settings);
    }

    /** Call once per bounded chunk, with a job-level deadline and concurrency limit outside. */
    public static String readClock() throws SQLException, IOException, ClassNotFoundException {
        try (Connection connection = connect()) {
            connection.setAutoCommit(false);
            boolean commitStarted = false;
            try {
                String result;
                try (PreparedStatement statement = connection.prepareStatement(
                        "SELECT /*+ MAX_EXECUTION_TIME(90000) */ CURRENT_TIMESTAMP")) {
                    statement.setQueryTimeout(120); // seconds, unlike socketTimeout (milliseconds)
                    try (ResultSet rows = statement.executeQuery()) {
                        if (!rows.next()) {
                            throw new SQLException("Expected one row");
                        }
                        result = rows.getString(1);
                    }
                }
                // Real jobs persist their business changes and checkpoint in this transaction.
                commitStarted = true;
                connection.commit();
                return result;
            } catch (SQLException failure) {
                try {
                    connection.rollback();
                } catch (SQLException rollbackFailure) {
                    failure.addSuppressed(rollbackFailure);
                }
                if (commitStarted) {
                    throw new SQLException("Commit outcome unknown; reconcile by business ID before retry", failure);
                }
                throw failure;
            }
        }
    }
}
