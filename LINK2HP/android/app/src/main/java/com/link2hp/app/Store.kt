package com.link2hp.app

import android.content.ContentValues
import android.content.Context
import android.database.sqlite.SQLiteDatabase
import android.database.sqlite.SQLiteOpenHelper
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import android.util.Base64
import java.security.KeyStore
import java.security.MessageDigest
import java.util.UUID
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec

internal data class Item(val id:String,val kind:String,val payload:String,val state:String,val reason:String)

internal class Store(private val ctx:Context):SQLiteOpenHelper(ctx,"link2hp.db",null,1) {
    override fun onCreate(db:SQLiteDatabase) {
        db.execSQL("CREATE TABLE outbox(id TEXT PRIMARY KEY, fingerprint TEXT UNIQUE NOT NULL, kind TEXT NOT NULL, payload TEXT NOT NULL, state TEXT NOT NULL, reason TEXT NOT NULL DEFAULT '', created INTEGER NOT NULL)")
    }
    override fun onUpgrade(db:SQLiteDatabase,oldVersion:Int,newVersion:Int) {}
    fun save(kind:String,payload:String):Boolean {
        val digest=MessageDigest.getInstance("SHA-256").digest((kind+"\n"+payload).toByteArray()).joinToString(""){ "%02x".format(it) }
        val data=ContentValues().apply {
            put("id",UUID.randomUUID().toString());put("fingerprint",digest)
            put("kind",kind);put("payload",encrypt(payload))
            put("state","QUEUED_PHONE");put("created",System.currentTimeMillis())
        }
        return writableDatabase.insertWithOnConflict("outbox",null,data,SQLiteDatabase.CONFLICT_IGNORE)!=-1L
    }
    fun rows(onlyPending:Boolean=false):List<Item> {
        val results=mutableListOf<Item>()
        val filter=if(onlyPending)"WHERE state='QUEUED_PHONE'" else ""
        readableDatabase.rawQuery("SELECT id,kind,payload,state,reason FROM outbox $filter ORDER BY created DESC LIMIT 70",null).use { c ->
            while(c.moveToNext())results+=Item(c.getString(0),c.getString(1),decrypt(c.getString(2)),c.getString(3),c.getString(4))
        }
        return results
    }
    fun update(id:String,state:String,reason:String="") {
        writableDatabase.execSQL("UPDATE outbox SET state=?,reason=? WHERE id=?", arrayOf(state,reason.take(120),id))
    }
    fun savePair(value:String){ctx.getSharedPreferences("link2hp",Context.MODE_PRIVATE).edit().putString("pair",encrypt(value)).apply()}
    fun pair():String? {
        val value=ctx.getSharedPreferences("link2hp",Context.MODE_PRIVATE).getString("pair",null) ?: return null
        return decrypt(value)
    }
    fun allowMetered():Boolean=ctx.getSharedPreferences("link2hp",Context.MODE_PRIVATE).getBoolean("metered",false)
    fun setMetered(allow:Boolean){ctx.getSharedPreferences("link2hp",Context.MODE_PRIVATE).edit().putBoolean("metered",allow).apply()}
    private fun key():SecretKey {
        val ks=KeyStore.getInstance("AndroidKeyStore").apply{load(null)}
        (ks.getKey("link2hp_secret",null) as? SecretKey)?.let{return it}
        return KeyGenerator.getInstance("AES","AndroidKeyStore").run {
            init(KeyGenParameterSpec.Builder("link2hp_secret",KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT)
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE).build())
            generateKey()
        }
    }
    private fun encrypt(text:String):String {
        val cipher=Cipher.getInstance("AES/GCM/NoPadding").apply{init(Cipher.ENCRYPT_MODE,key())}
        return Base64.encodeToString(cipher.iv+cipher.doFinal(text.toByteArray(Charsets.UTF_8)),Base64.NO_WRAP)
    }
    private fun decrypt(encrypted:String):String {
        val b=Base64.decode(encrypted,Base64.NO_WRAP)
        val cipher=Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.DECRYPT_MODE,key(),GCMParameterSpec(128,b.copyOfRange(0,12)))
        return String(cipher.doFinal(b.copyOfRange(12,b.size)),Charsets.UTF_8)
    }
}
