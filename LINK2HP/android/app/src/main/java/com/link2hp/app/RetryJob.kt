package com.link2hp.app

import android.app.job.JobInfo
import android.app.job.JobParameters
import android.app.job.JobScheduler
import android.app.job.JobService
import android.content.ComponentName
import android.content.Context

class RetryJob:JobService(){
    override fun onStartJob(params:JobParameters):Boolean {
        Thread {
            val retry=try{Api.process(this,false)}catch(_:Exception){true}
            jobFinished(params,retry)
        }.start()
        return true
    }
    override fun onStopJob(params:JobParameters):Boolean=true
    companion object {
        fun schedule(ctx:Context){
            val scheduler=ctx.getSystemService(Context.JOB_SCHEDULER_SERVICE) as JobScheduler
            val unmetered=!Store(ctx).allowMetered()
            val request=JobInfo.Builder(93210,ComponentName(ctx,RetryJob::class.java))
                .setRequiredNetworkType(if(unmetered)JobInfo.NETWORK_TYPE_UNMETERED else JobInfo.NETWORK_TYPE_ANY)
                .setBackoffCriteria(30_000,JobInfo.BACKOFF_POLICY_EXPONENTIAL)
                .setPersisted(true)
                .build()
            scheduler.schedule(request)
        }
    }
}
