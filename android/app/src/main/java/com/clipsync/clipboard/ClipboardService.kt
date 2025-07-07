package com.clipsync.clipboard

import android.app.*
import android.content.*
import android.os.*
import android.util.Log
import android.widget.Toast
import android.content.ClipboardManager
import androidx.core.app.NotificationCompat
import com.clipsync.R

class ClipboardService : Service() {

    private lateinit var clipboardManager: ClipboardManager
    private lateinit var listener: ClipboardManager.OnPrimaryClipChangedListener

    override fun onCreate() {
        super.onCreate()
        Log.d("ClipboardService", "Service created")

        // Initialize clipboard manager
        clipboardManager = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager

        // Listener for clipboard changes
        listener = ClipboardManager.OnPrimaryClipChangedListener {
            val clip = clipboardManager.primaryClip
            val item = clip?.getItemAt(0)?.text?.toString()

            if (!item.isNullOrBlank()) {
                Log.d("ClipboardService", "Clipboard changed: $item")
                Toast.makeText(this, "Copied: $item", Toast.LENGTH_SHORT).show()

                // TODO: Send this to Windows via HTTP POST
            }
        }

        clipboardManager.addPrimaryClipChangedListener(listener)
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Log.d("ClipboardService", "Service started")

        startForeground(NOTIF_ID, createNotification())
        return START_STICKY
    }

    override fun onDestroy() {
        super.onDestroy()
        clipboardManager.removePrimaryClipChangedListener(listener)
        Log.d("ClipboardService", "Service destroyed")
    }

    override fun onBind(intent: Intent?): IBinder? = null

    private fun createNotification(): Notification {
        val channelId = "ClipSyncChannel"
        val channelName = "ClipSync Clipboard Monitor"

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val chan = NotificationChannel(channelId, channelName, NotificationManager.IMPORTANCE_LOW)
            val manager = getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(chan)
        }

        val notifIntent = Intent(this, Class.forName("com.clipsync.MainActivity"))
        val pendingIntent = PendingIntent.getActivity(this, 0, notifIntent, PendingIntent.FLAG_IMMUTABLE)

        return NotificationCompat.Builder(this, channelId)
            .setContentTitle("ClipSync Running")
            .setContentText("Monitoring clipboard...")
            .setSmallIcon(R.drawable.ic_launcher_foreground)
            .setContentIntent(pendingIntent)
            .build()
    }

    companion object {
        private const val NOTIF_ID = 101
    }
}
