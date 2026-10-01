import { createClient } from '@supabase/supabase-js'
const supabase = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL, process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY)

export default async function handler(req,res){
  try{
    const user_id = req.query.user_id
    if(!user_id) return res.status(400).json({error:'falta user_id'})
    const { data, error } = await supabase.from('user_data').select('data').eq('user_id', user_id).single()
    if(error && error.code !== 'PGRST116') return res.status(500).json({error:error.message})
    return res.status(200).json({data: data?.data || {}})
  }catch(e){ return res.status(500).json({error:e.message}) }
}
