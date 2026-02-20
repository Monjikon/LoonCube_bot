package ru.mclink.plugin.commands;

import com.google.gson.JsonObject;
import org.bukkit.command.*;
import org.bukkit.entity.Player;
import ru.mclink.plugin.MCLinkPlugin;

public class LinkCommand implements CommandExecutor {

    private final MCLinkPlugin plugin;

    public LinkCommand(MCLinkPlugin plugin) {
        this.plugin = plugin;
    }

    @Override
    public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        if (!(sender instanceof Player)) {
            sender.sendMessage("§cЭту команду могут использовать только игроки.");
            return true;
        }

        Player player = (Player) sender;

        // Проверяем, не привязан ли уже аккаунт
        plugin.getApiClient()
            .checkLink(player.getUniqueId().toString())
            .thenAccept(resp -> {
                if (resp != null && resp.has("linked") && resp.get("linked").getAsBoolean()) {
                    String platform = resp.has("platform") ? resp.get("platform").getAsString() : "?";
                    player.sendMessage(plugin.msg("already_linked", "platform", platform));
                    return;
                }

                // Генерируем код
                plugin.getApiClient()
                    .generateCode(player.getUniqueId().toString(), player.getName())
                    .thenAccept(code -> {
                        if (code == null) {
                            player.sendMessage(plugin.msg("error"));
                            return;
                        }
                        // Отправляем сообщение игроку (в основной поток)
                        plugin.getServer().getScheduler().runTask(plugin, () -> {
                            player.sendMessage(plugin.msg("code_generated", "code", code));
                            player.sendMessage(plugin.msg("code_hint", "code", code));
                        });
                    });
            });

        return true;
    }
}
