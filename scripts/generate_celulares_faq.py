import os
import json

faq_data = [
    {
        "question": "Qual o melhor celular para comprar em 2026?",
        "answer": "O 'melhor' celular depende do seu orçamento e necessidades. Para quem busca o topo de linha, modelos como o iPhone 16 Pro Max ou Samsung Galaxy S26 Ultra são excelentes. Para custo-benefício, o Xiaomi Redmi Note 15 Pro ou Samsung Galaxy A57 se destacam. Nosso guia completo 'Como Escolher um Celular' pode te ajudar a decidir."
    },
    {
        "question": "Celular Android ou iPhone: qual escolher?",
        "answer": "Android oferece maior flexibilidade, personalização e uma vasta gama de preços e modelos. iPhones (iOS) são conhecidos pela simplicidade, ecossistema integrado, segurança e atualizações de software de longo prazo. A escolha ideal depende da sua preferência por liberdade de customização (Android) ou integração e estabilidade (iOS)."
    },
    {
        "question": "O que é importante considerar na câmera de um celular?",
        "answer": "Para uma boa câmera, observe a quantidade de megapixels (MP), mas principalmente a abertura da lente (quanto menor o número f/, melhor), a presença de Estabilização Óptica de Imagem (OIS) e a versatilidade dos sensores (ultrawide, macro, telefoto). Recursos de software como Modo Noturno e HDR também fazem grande diferença."
    },
    {
        "question": "Quanto de RAM é necessário em um celular?",
        "answer": "Para uso básico (redes sociais, mensagens), 4GB de RAM são suficientes. Para uso moderado (jogos leves, multitarefas), 6GB a 8GB oferecem fluidez. Para jogos pesados, edição de vídeo ou uso intenso, 8GB a 12GB de RAM são ideais para garantir o melhor desempenho."
    },
    {
        "question": "Vale a pena comprar um celular 5G em 2026?",
        "answer": "Sim, se a cobertura 5G já estiver disponível na sua região e você busca velocidades de internet ultrarrápidas. Mesmo que a cobertura ainda seja limitada, um celular 5G garante que você estará preparado para o futuro. Verifique a compatibilidade com as bandas 5G do Brasil antes de comprar."
    }
]

faq_html = ""
faq_schema_items = []

for item in faq_data:
    faq_html += f'''
    <div class="faq-item">
        <p class="faq-question">{item["question"]}</p>
        <p class="faq-answer">{item["answer"]}</p>
    </div>
    '''
    faq_schema_items.append({
        "@type": "Question",
        "name": item["question"],
        "acceptedAnswer": {
            "@type": "Answer",
            "text": item["answer"]
        }
    })

# Salvar HTML do FAQ
with open("noticias/posts/celulares-faq.html", "w", encoding="utf-8") as f:
    f.write(faq_html)

# Salvar JSON-LD do Schema FAQ
with open("data/schema/celulares-faq-schema.json", "w", encoding="utf-8") as f:
    json.dump(faq_schema_items, f, ensure_ascii=False, indent=2)

print("Conteúdo FAQ e Schema FAQ para Celulares gerados com sucesso.")
