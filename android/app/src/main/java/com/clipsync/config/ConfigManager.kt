package com.clipsync.config

import android.content.Context
import android.content.SharedPreferences

object ConfigManager {
    private const val PREF_NAME = "ClipSyncConfig"
    private const val KEY_IP = "windows_ip"
    private const val KEY_PORT = "windows_port"

    private fun getPrefs(context: Context): SharedPreferences {
        return context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE)
    }

    fun saveConfig(context: Context, ip: String, port: String) {
        getPrefs(context).edit()
            .putString(KEY_IP, ip)
            .putString(KEY_PORT, port)
            .apply()
    }

    fun getIP(context: Context): String? {
        return getPrefs(context).getString(KEY_IP, null)
    }

    fun getPort(context: Context): String? {
        return getPrefs(context).getString(KEY_PORT, null)
    }

    fun isConfigSet(context: Context): Boolean {
        return getIP(context) != null && getPort(context) != null
    }
}
