package com.clipsync.config
import android.content.Context
import android.content.SharedPreferences
import android.util.Log
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.TextView
import android.view.ViewGroup
import android.widget.CheckBox
import android.widget.Toast
import java.net.InetAddress
import java.net.NetworkInterface
import java.util.Collections

class ConfigManager(private val context: Context) {
    
    companion object {
        private const val TAG = "ConfigManager"
        private const val PREFS_NAME = "clipsync_config"
        private const val KEY_SERVER_IP = "server_ip"
        private const val KEY_SERVER_PORT = "server_port"
        private const val KEY_IS_CONFIGURED = "is_configured"
        private const val KEY_AUTO_CONNECT = "auto_connect"
        private const val DEFAULT_PORT = 8080
        private const val DEFAULT_IP = "192.168.1.100"
    }
    
    private val sharedPreferences: SharedPreferences = 
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    
    /**
     * Data class to hold server configuration
     */
    data class ServerConfig(
        val ip: String,
        val port: Int,
        val isConfigured: Boolean = false,
        val autoConnect: Boolean = false
    )
    
    /**
     * Enum for configuration choice
     */
    enum class ConfigChoice {
        USE_EXISTING,
        NEW_CONFIG
    }
    
    /**
     * Gets the current server configuration from SharedPreferences
     */
    fun getServerConfig(): ServerConfig {
        return ServerConfig(
            ip = sharedPreferences.getString(KEY_SERVER_IP, DEFAULT_IP) ?: DEFAULT_IP,
            port = sharedPreferences.getInt(KEY_SERVER_PORT, DEFAULT_PORT),
            isConfigured = sharedPreferences.getBoolean(KEY_IS_CONFIGURED, false),
            autoConnect = sharedPreferences.getBoolean(KEY_AUTO_CONNECT, false)
        )
    }
    
    /**
     * Saves server configuration to SharedPreferences
     */
    fun saveServerConfig(config: ServerConfig) {
        with(sharedPreferences.edit()) {
            putString(KEY_SERVER_IP, config.ip)
            putInt(KEY_SERVER_PORT, config.port)
            putBoolean(KEY_IS_CONFIGURED, config.isConfigured)
            putBoolean(KEY_AUTO_CONNECT, config.autoConnect)
            apply()
        }
        Log.d(TAG, "Server configuration saved: ${config.ip}:${config.port}")
    }
    
    /**
     * Checks if the app has been configured with server details
     */
    fun isConfigured(): Boolean {
        return sharedPreferences.getBoolean(KEY_IS_CONFIGURED, false)
    }
    
    /**
     * Clears all configuration data
     */
    fun clearConfig() {
        with(sharedPreferences.edit()) {
            clear()
            apply()
        }
        Log.d(TAG, "Configuration cleared")
    }
    
    /**
     * Prompts user to configure server settings with dialog
     * Returns a CompletableDeferred that resolves when user completes configuration
     */
    suspend fun promptForConfiguration(activity: AppCompatActivity): ServerConfig? {
        return withContext(Dispatchers.Main) {
            val deferred = CompletableDeferred<ServerConfig?>()
            
            val currentConfig = getServerConfig()
            
            // Create dialog layout
            val dialogLayout = LinearLayout(activity).apply {
                orientation = LinearLayout.VERTICAL
                setPadding(50, 40, 50, 40)
            }
            
            // Title
            val titleView = TextView(activity).apply {
                text = "Configure ClipSync Server"
                textSize = 18f
                setPadding(0, 0, 0, 20)
            }
            dialogLayout.addView(titleView)
            
            // Current config display (if exists)
            if (currentConfig.isConfigured) {
                val currentConfigView = TextView(activity).apply {
                    text = "Current: ${currentConfig.ip}:${currentConfig.port}"
                    textSize = 14f
                    setPadding(0, 0, 0, 10)
                }
                dialogLayout.addView(currentConfigView)
            }
            
            // IP Address input
            val ipLabel = TextView(activity).apply {
                text = "Server IP Address:"
                setPadding(0, 10, 0, 5)
            }
            dialogLayout.addView(ipLabel)
            
            val ipEditText = EditText(activity).apply {
                hint = "e.g., 192.168.1.100"
                setText(if (currentConfig.isConfigured) currentConfig.ip else getLocalIPAddress())
                layoutParams = LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT,
                    ViewGroup.LayoutParams.WRAP_CONTENT
                )
            }
            dialogLayout.addView(ipEditText)
            
            // Port input
            val portLabel = TextView(activity).apply {
                text = "Server Port:"
                setPadding(0, 20, 0, 5)
            }
            dialogLayout.addView(portLabel)
            
            val portEditText = EditText(activity).apply {
                hint = "e.g., 8080"
                setText(currentConfig.port.toString())
                inputType = android.text.InputType.TYPE_CLASS_NUMBER
                layoutParams = LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT,
                    ViewGroup.LayoutParams.WRAP_CONTENT
                )
            }
            dialogLayout.addView(portEditText)
            
            // Auto connect checkbox
            val autoConnectLabel = TextView(activity).apply {
                text = "Auto-connect on app start"
                setPadding(0, 20, 0, 5)
            }
            dialogLayout.addView(autoConnectLabel)
            
            val autoConnectCheckbox = CheckBox(activity).apply {
                isChecked = currentConfig.autoConnect
            }
            dialogLayout.addView(autoConnectCheckbox)
            
            // Create and show dialog
            val dialog = AlertDialog.Builder(activity)
                .setTitle("Server Configuration")
                .setView(dialogLayout)
                .setPositiveButton("Save") { _, _ ->
                    val ip = ipEditText.text.toString().trim()
                    val portText = portEditText.text.toString().trim()
                    
                    if (ip.isEmpty()) {
                        Toast.makeText(activity, "IP address cannot be empty", Toast.LENGTH_SHORT).show()
                        deferred.complete(null)
                        return@setPositiveButton
                    }
                    
                    if (!isValidIPAddress(ip)) {
                        Toast.makeText(activity, "Invalid IP address format", Toast.LENGTH_SHORT).show()
                        deferred.complete(null)
                        return@setPositiveButton
                    }
                    
                    val port = try {
                        portText.toInt()
                    } catch (e: NumberFormatException) {
                        Toast.makeText(activity, "Invalid port number", Toast.LENGTH_SHORT).show()
                        deferred.complete(null)
                        return@setPositiveButton
                    }
                    
                    if (!isValidPort(port)) {
                        Toast.makeText(activity, "Port must be between 1 and 65535", Toast.LENGTH_SHORT).show()
                        deferred.complete(null)
                        return@setPositiveButton
                    }
                    
                    val newConfig = ServerConfig(
                        ip = ip,
                        port = port,
                        isConfigured = true,
                        autoConnect = autoConnectCheckbox.isChecked
                    )
                    
                    saveServerConfig(newConfig)
                    Toast.makeText(activity, "Configuration saved successfully!", Toast.LENGTH_SHORT).show()
                    deferred.complete(newConfig)
                }
                .setNegativeButton("Cancel") { _, _ ->
                    deferred.complete(null)
                }
                .setNeutralButton("Use Existing") { _, _ ->
                    if (currentConfig.isConfigured) {
                        deferred.complete(currentConfig)
                    } else {
                        deferred.complete(null)
                    }
                }
                .setCancelable(false)
                .create()
            
            // Hide "Use Existing" button if no existing config
            if (!currentConfig.isConfigured) {
                dialog.setOnShowListener {
                    dialog.getButton(AlertDialog.BUTTON_NEUTRAL).visibility = android.view.View.GONE
                }
            }
            
            dialog.show()
            deferred.await()
        }
    }
    
    /**
     * Shows a simple dialog to choose between existing config or new config
     */
    suspend fun promptConfigChoice(activity: AppCompatActivity): ConfigChoice? {
        return withContext(Dispatchers.Main) {
            val deferred = CompletableDeferred<ConfigChoice?>()
            
            val currentConfig = getServerConfig()
            
            if (!currentConfig.isConfigured) {
                // No existing config, directly return new config choice
                return@withContext ConfigChoice.NEW_CONFIG
            }
            
            AlertDialog.Builder(activity)
                .setTitle("Server Configuration")
                .setMessage("Use existing configuration (${currentConfig.ip}:${currentConfig.port}) or enter new settings?")
                .setPositiveButton("Use Existing") { _, _ ->
                    deferred.complete(ConfigChoice.USE_EXISTING)
                }
                .setNegativeButton("New Config") { _, _ ->
                    deferred.complete(ConfigChoice.NEW_CONFIG)
                }
                .setNeutralButton("Cancel") { _, _ ->
                    deferred.complete(null)
                }
                .setCancelable(false)
                .show()
            
            deferred.await()
        }
    }
    
    /**
     * Validates IP address format
     */
    fun isValidIPAddress(ip: String): Boolean {
        return try {
            InetAddress.getByName(ip)
            true
        } catch (e: Exception) {
            false
        }
    }
    
    /**
     * Validates port number
     */
    fun isValidPort(port: Int): Boolean {
        return port in 1..65535
    }
    
    /**
     * Gets the local IP address of the device
     */
    private fun getLocalIPAddress(): String {
        try {
            val interfaces = Collections.list(NetworkInterface.getNetworkInterfaces())
            for (networkInterface in interfaces) {
                val addresses = Collections.list(networkInterface.inetAddresses)
                for (address in addresses) {
                    if (!address.isLoopbackAddress && address.address.size == 4) {
                        return address.hostAddress ?: DEFAULT_IP
                    }
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error getting local IP address", e)
        }
        return DEFAULT_IP
    }
    
    /**
     * Updates only the auto-connect setting
     */
    fun updateAutoConnect(autoConnect: Boolean) {
        with(sharedPreferences.edit()) {
            putBoolean(KEY_AUTO_CONNECT, autoConnect)
            apply()
        }
        Log.d(TAG, "Auto-connect updated: $autoConnect")
    }
    
    /**
     * Shows configuration status as toast
     */
    fun showConfigStatus() {
        val config = getServerConfig()
        val status = if (config.isConfigured) {
            "Server: ${config.ip}:${config.port}\nAuto-connect: ${if (config.autoConnect) "Enabled" else "Disabled"}"
        } else {
            "Not configured"
        }
        Toast.makeText(context, status, Toast.LENGTH_LONG).show()
    }
    
    /**
     * Resets configuration with confirmation dialog
     */
    fun resetConfiguration(activity: AppCompatActivity, onReset: (() -> Unit)? = null) {
        AlertDialog.Builder(activity)
            .setTitle("Reset Configuration")
            .setMessage("Are you sure you want to reset all configuration settings?")
            .setPositiveButton("Reset") { _, _ ->
                clearConfig()
                onReset?.invoke()
                Toast.makeText(activity, "Configuration reset successfully", Toast.LENGTH_SHORT).show()
            }
            .setNegativeButton("Cancel", null)
            .show()
    }
    
    /**
     * Exports configuration as a string (for backup/sharing)
     */
    fun exportConfig(): String {
        val config = getServerConfig()
        return "${config.ip}:${config.port}:${config.autoConnect}"
    }
    
    /**
     * Imports configuration from string (for backup/sharing)
     */
    fun importConfig(configString: String): Boolean {
        return try {
            val parts = configString.split(":")
            if (parts.size >= 2) {
                val ip = parts[0]
                val port = parts[1].toInt()
                val autoConnect = if (parts.size > 2) parts[2].toBoolean() else false
                
                if (isValidIPAddress(ip) && isValidPort(port)) {
                    val config = ServerConfig(
                        ip = ip,
                        port = port,
                        isConfigured = true,
                        autoConnect = autoConnect
                    )
                    saveServerConfig(config)
                    true
                } else {
                    false
                }
            } else {
                false
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error importing config", e)
            false
        }
    }
    
    /**
     * Initializes configuration on app startup
     * Handles auto-connect and prompts user if needed
     */
    suspend fun initializeConfig(activity: AppCompatActivity, forcePrompt: Boolean = false): ServerConfig? {
        return withContext(Dispatchers.Main) {
            val currentConfig = getServerConfig()
            
            when {
                forcePrompt -> {
                    // Force show configuration dialog
                    promptForConfiguration(activity)
                }
                !currentConfig.isConfigured -> {
                    // No existing configuration, prompt user
                    Toast.makeText(context, "Please configure server settings", Toast.LENGTH_SHORT).show()
                    promptForConfiguration(activity)
                }
                currentConfig.autoConnect -> {
                    // Auto-connect enabled, use existing config
                    currentConfig
                }
                else -> {
                    // Ask user what to do
                    when (promptConfigChoice(activity)) {
                        ConfigChoice.USE_EXISTING -> currentConfig
                        ConfigChoice.NEW_CONFIG -> promptForConfiguration(activity)
                        null -> null
                    }
                }
            }
        }
    }
    
    /**
     * Gets available network interfaces for debugging
     */
    fun getNetworkInfo(): List<String> {
        val networkInfo = mutableListOf<String>()
        try {
            val interfaces = Collections.list(NetworkInterface.getNetworkInterfaces())
            for (networkInterface in interfaces) {
                if (networkInterface.isUp && !networkInterface.isLoopback) {
                    val addresses = Collections.list(networkInterface.inetAddresses)
                    for (address in addresses) {
                        if (address.address.size == 4) { // IPv4
                            networkInfo.add("${networkInterface.name}: ${address.hostAddress}")
                        }
                    }
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error getting network info", e)
        }
        return networkInfo
    }
}