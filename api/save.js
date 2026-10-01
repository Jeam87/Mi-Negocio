import { createClient } from '@supabase/supabase-js'
const supabase = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL, process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY)

export default async function handler(req,res){
  if(req.method !== 'POST') return res.status(405).json({error:'method not allowed'})
  try{
    const { user_id, data } = req.body
    if(!user_id) return res.status(400).json({error:'falta user_id'})
    const { error } = await supabase.from('user_data').upsert({ user_id, data, updated_at: new Date().toISOString() }, {onConflict:'user_id'})
    if(error) return res.status(500).json({error:error.message})
    return res.status(200).json({ok:true})
  }catch(e){ return res.status(500).json({error:e.message}) }
}
