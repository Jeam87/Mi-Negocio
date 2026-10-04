import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

export default async function Tienda({ params }: { params: { user_id: string } }) {
  const { data: products } = await supabase
    .from('products')
    .select('*')
    .eq('user_id', params.user_id)
    .gt('stock', 0)

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-md mx-auto bg-white rounded-2xl shadow p-5">
        <h1 className="text-2xl font-bold">🛒 Mi Tienda</h1>
        <p className="text-gray-500 mb-5 text-sm">Pide por WhatsApp - Entrega en Jacona</p>
        
        <div className="space-y-3">
          {products?.map((p: any) => (
            <div key={p.id} className="flex justify-between items-center border rounded-xl p-4">
              <div>
                <h2 className="font-bold">{p.name}</h2>
                <p className="text-xs text-gray-400">{p.category} • Stock: {p.stock}</p>
                <p className="text-green-600 font-bold text-lg">${p.price}</p>
              </div>
              <a
                href={`https://wa.me/523521009999?text=Hola, quiero pedir: ${p.name} - $${p.price}`}
                target="_blank"
                className="bg-green-500 text-white px-4 py-2 rounded-full text-sm font-bold"
              >
                Pedir
              </a>
            </div>
          ))}
        </div>

        {(!products || products.length === 0) && (
          <p className="text-center py-10 text-gray-400">No hay productos</p>
        )}
      </div>
    </div>
  )
}
