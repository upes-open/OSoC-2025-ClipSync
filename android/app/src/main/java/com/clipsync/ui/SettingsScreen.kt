package com.clipsync.ui

import android.widget.Toast
import androidx.compose.foundation.layout.*
import androidx.compose.material.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.clipsync.config.ConfigManager

@Composable
fun SettingsScreen(onConfigSaved: () -> Unit) {
    val context = LocalContext.current
    var ip by remember { mutableStateOf("") }
    var port by remember { mutableStateOf("") }

    Column(modifier = Modifier.padding(16.dp)) {
        Text("Enter Windows Machine IP and Port", style = MaterialTheme.typography.h6)
        Spacer(modifier = Modifier.height(8.dp))

        OutlinedTextField(
            value = ip,
            onValueChange = { ip = it },
            label = { Text("Windows IP (e.g. 192.168.1.100)") },
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(8.dp))

        OutlinedTextField(
            value = port,
            onValueChange = { port = it },
            label = { Text("Port (e.g. 5000)") },
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(16.dp))

        Button(
            onClick = {
                if (ip.isNotBlank() && port.isNotBlank()) {
                    ConfigManager.saveConfig(context, ip, port)
                    Toast.makeText(context, "Saved!", Toast.LENGTH_SHORT).show()
                    onConfigSaved()
                } else {
                    Toast.makeText(context, "Please enter both fields", Toast.LENGTH_SHORT).show()
                }
            },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Save")
        }
    }
}
