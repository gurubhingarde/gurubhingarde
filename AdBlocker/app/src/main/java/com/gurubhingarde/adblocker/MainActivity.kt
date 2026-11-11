package com.gurubhingarde.adblocker

import android.app.Activity
import android.content.Intent
import android.graphics.Typeface
import android.net.VpnService
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.Gravity
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast

class MainActivity : Activity() {

    private lateinit var status: TextView
    private lateinit var stats: TextView
    private lateinit var toggle: Button
    private lateinit var update: Button
    private val ui = Handler(Looper.getMainLooper())
    private val tick = object : Runnable {
        override fun run() {
            refresh()
            ui.postDelayed(this, 1000)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val pad = (24 * resources.displayMetrics.density).toInt()
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            setPadding(pad, pad, pad, pad)
        }
        val title = TextView(this).apply {
            text = "AdBlocker"
            textSize = 32f
            typeface = Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER
        }
        status = TextView(this).apply { textSize = 18f; gravity = Gravity.CENTER; setPadding(0, pad, 0, pad / 2) }
        stats = TextView(this).apply { textSize = 14f; gravity = Gravity.CENTER; setPadding(0, 0, 0, pad) }
        toggle = Button(this).apply { setOnClickListener { onToggle() } }
        update = Button(this).apply {
            text = "Update ad list"
            setOnClickListener { onUpdate() }
        }
        listOf(title, status, stats, toggle, update).forEach { root.addView(it) }
        setContentView(root)
    }

    override fun onResume() {
        super.onResume()
        ui.post(tick)
    }

    override fun onPause() {
        ui.removeCallbacks(tick)
        super.onPause()
    }

    private fun refresh() {
        val on = AdBlockVpnService.running
        status.text = if (on) "Protection ON" else "Protection OFF"
        toggle.text = if (on) "Turn off" else "Turn on"
        stats.text = "Blocked: ${AdBlockVpnService.blocked.get()}   Allowed: ${AdBlockVpnService.allowed.get()}"
    }

    private fun onToggle() {
        if (AdBlockVpnService.running) {
            startService(Intent(this, AdBlockVpnService::class.java).setAction(AdBlockVpnService.ACTION_STOP))
            return
        }
        val consent = VpnService.prepare(this) // system dialog asking for VPN permission
        if (consent != null) startActivityForResult(consent, 1) else startVpn()
    }

    @Deprecated("Deprecated in Java")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == 1 && resultCode == RESULT_OK) startVpn()
    }

    private fun startVpn() {
        startService(Intent(this, AdBlockVpnService::class.java))
    }

    private fun onUpdate() {
        update.isEnabled = false
        Thread {
            val msg = try {
                Blocklist.update(applicationContext)
                "Loaded ${Blocklist.size} blocked domains"
            } catch (e: Exception) {
                "Update failed: ${e.message}"
            }
            runOnUiThread {
                update.isEnabled = true
                Toast.makeText(this, msg, Toast.LENGTH_LONG).show()
            }
        }.start()
    }
}
