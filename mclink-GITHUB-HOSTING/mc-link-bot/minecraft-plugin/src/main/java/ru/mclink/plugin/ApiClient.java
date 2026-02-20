package ru.mclink.plugin;

import com.google.gson.Gson;
import com.google.gson.JsonObject;

import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.CompletableFuture;

/**
 * Клиент для REST API Python-бота.
 */
public class ApiClient {

    private final String baseUrl;
    private final String secret;
    private final int    timeoutMs;
    private final Gson   gson = new Gson();

    public ApiClient(String baseUrl, String secret, int timeoutSec) {
        this.baseUrl    = baseUrl.replaceAll("/$", "");
        this.secret     = secret;
        this.timeoutMs  = timeoutSec * 1000;
    }

    // ── Генерация кода ────────────────────────────────────────────────────────

    /** Асинхронно генерирует код привязки. Возвращает код или null при ошибке. */
    public CompletableFuture<String> generateCode(String uuid, String nick) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                JsonObject body = new JsonObject();
                body.addProperty("uuid", uuid);
                body.addProperty("nick", nick);

                JsonObject resp = post("/api/generate_code", body.toString());
                return resp != null && resp.has("code") ? resp.get("code").getAsString() : null;
            } catch (Exception e) {
                MCLinkPlugin.getInstance().getLogger().warning("generateCode error: " + e.getMessage());
                return null;
            }
        });
    }

    // ── Проверка привязки ─────────────────────────────────────────────────────

    public CompletableFuture<JsonObject> checkLink(String uuid) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                return get("/api/check_link?uuid=" + URLEncoder.encode(uuid, "UTF-8"));
            } catch (Exception e) {
                MCLinkPlugin.getInstance().getLogger().warning("checkLink error: " + e.getMessage());
                return null;
            }
        });
    }

    // ── HTTP утилиты ─────────────────────────────────────────────────────────

    private JsonObject post(String path, String jsonBody) throws IOException {
        URL url = new URL(baseUrl + path);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("POST");
        conn.setRequestProperty("Content-Type", "application/json");
        conn.setRequestProperty("X-API-Secret", secret);
        conn.setConnectTimeout(timeoutMs);
        conn.setReadTimeout(timeoutMs);
        conn.setDoOutput(true);

        try (OutputStream os = conn.getOutputStream()) {
            os.write(jsonBody.getBytes(StandardCharsets.UTF_8));
        }
        return readResponse(conn);
    }

    private JsonObject get(String path) throws IOException {
        URL url = new URL(baseUrl + path);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("GET");
        conn.setRequestProperty("X-API-Secret", secret);
        conn.setConnectTimeout(timeoutMs);
        conn.setReadTimeout(timeoutMs);
        return readResponse(conn);
    }

    private JsonObject readResponse(HttpURLConnection conn) throws IOException {
        int code = conn.getResponseCode();
        InputStream is = code >= 400 ? conn.getErrorStream() : conn.getInputStream();
        if (is == null) return null;

        try (BufferedReader br = new BufferedReader(new InputStreamReader(is, StandardCharsets.UTF_8))) {
            StringBuilder sb = new StringBuilder();
            String line;
            while ((line = br.readLine()) != null) sb.append(line);
            return gson.fromJson(sb.toString(), JsonObject.class);
        }
    }
}
