package com.clipsync

import android.content.Intent
import android.os.Build
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.material.Text
import androidx.compose.material.MaterialTheme
import androidx.compose.material.Surface
import androidx.compose.runtime.Composable
import androidx.compose.ui.tooling.preview.Preview
import com.clipsync.clipboard.ClipboardService
import com.clipsync.config.ConfigManager
import com.clipsync.ui.SettingsScreen
import com.clipsync.ui.theme.ClipSyncTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            ClipSyncTheme {
                Surface(color = MaterialTheme.colors.background) {
                    if (!ConfigManager.isConfigSet(this)) {
                        SettingsScreen {
                            recreate() // Restart activity after saving config
                        }
                    } else {
                        StartClipboardService()
                        DashboardUI()
                    }
                }
            }
        }
    }

    private fun StartClipboardService() {
        val serviceIntent = Intent(this, ClipboardService::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(serviceIntent)
        } else {
            startService(serviceIntent)
        }
    }
}

@Composable
fun DashboardUI() {
    Text("Clipboard Sync is running.")
}

@Preview(showBackground = true)
@Composable
fun DefaultPreview() {
    ClipSyncTheme {
        DashboardUI()
    }
}

