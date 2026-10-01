export default async function handler(req, res) {
  const hasUrl = !! (process.env.NEXT_PUBLIC_SUPABASE_URL || process.env.VITE_SUPABASE_URL || process.env.SUPABASE_URL);
  const hasAnon = !! (process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || process.env.VITE_SUPABASE_ANON_KEY);
  const hasService = !! (process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.VITE_SUPABASE_SERVICE_ROLE_KEY);
  
  let supabaseImport = "ok";
  try {
    await import('@supabase/supabase-js');
  } catch (e) {
    supabaseImport = "FALLO: " + e.message;
  }

  return res.json({
    hasUrl,
    hasAnon,
    hasService,
    supabaseImport,
    allEnvKeys: Object.keys(process.env).filter(k => k.toLowerCase().includes('supabase'))
  });
}
