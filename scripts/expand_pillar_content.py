import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / 'server' / '_core'))

# Simulação de expansão de conteúdo rica para os 5 produtos pilares
PILLAR_IDS = ['MLB17375584', 'MLB15238956', 'MLB4812143184', 'MLB24028629', 'MLB26000295']

PILLAR_CONTENT = {
    'MLB17375584': {
        'intro': "O Controle Sem Fio Microsoft para Xbox Series S, X, One e PC na cor Pulse Red não é apenas um acessório, mas uma extensão da experiência de jogo. Com um design refinado e ergonomia aprimorada, este controle se destaca tanto pela performance quanto pelo visual vibrante.",
        'features': "Este modelo traz o novo botão 'Compartilhar', que permite capturar e compartilhar conteúdo instantaneamente. O direcional híbrido oferece uma precisão incrível para jogos de luta e plataforma, enquanto as superfícies texturizadas nos gatilhos e botões superiores garantem uma pegada firme mesmo em sessões intensas.",
        'pros': "Conectividade Bluetooth rápida; Compatibilidade multiplataforma (Xbox, Windows, Android, iOS); Resposta tátil de alta qualidade; Design ergonômico premiado.",
        'cons': "Uso de pilhas AA por padrão (bateria recarregável vendida separadamente); Preço pode ser elevado fora de promoções.",
        'target': "Ideal para jogadores que buscam precisão competitiva e conforto para longas horas de gameplay, além de entusiastas que valorizam um setup com cores vibrantes.",
        'comparison': "Comparado ao modelo do Xbox One, o Series S/X possui latência reduzida e uma ergonomia ligeiramente menor, adaptando-se melhor a diferentes tamanhos de mãos.",
        'faq': [
            {"q": "Funciona no PC via Bluetooth?", "a": "Sim, ele é compatível com Windows 10 e 11 nativamente via Bluetooth ou cabo USB-C."},
            {"q": "Acompanha bateria recarregável?", "a": "Não, o controle utiliza 2 pilhas AA inclusas. O kit de bateria recarregável é vendido à parte."},
            {"q": "Tem entrada para fone de ouvido?", "a": "Sim, possui entrada padrão de 3.5mm para qualquer headset compatível."}
        ]
    },
    'MLB4812143184': {
        'intro': "A Creatina Monohidratada Pura 500g da Dark Lab é um dos suplementos mais estudados e eficazes para quem busca ganho de força e explosão muscular. Com alto grau de pureza, ela se tornou a favorita de atletas profissionais e amadores pelo seu custo-benefício imbatível.",
        'features': "O produto é composto 100% por creatina monohidratada, sem adição de açúcares, glúten ou conservantes. Sua moagem fina facilita a diluição em água ou sucos, garantindo uma absorção eficiente pelo organismo.",
        'pros': "Excelente custo-benefício por grama; Pureza testada em laboratório; Sem sabor, facilitando a mistura; Embalagem econômica de 500g.",
        'cons': "Pode empelotar se não for bem misturada; Requer uso constante para saturação muscular.",
        'target': "Indicada para praticantes de musculação, crossfit e esportes de alta intensidade que desejam melhorar o desempenho físico e a recuperação muscular.",
        'comparison': "Frente a marcas importadas, a Dark Lab entrega a mesma pureza monohidratada com um preço significativamente menor no mercado brasileiro.",
        'faq': [
            {"q": "Qual a dose diária recomendada?", "a": "Geralmente recomenda-se 3g a 5g por dia, todos os dias, inclusive nos dias de descanso."},
            {"q": "Precisa fazer fase de carga?", "a": "Não é obrigatório, mas pode acelerar os resultados iniciais. O uso contínuo é o mais importante."},
            {"q": "Creatina retém líquido?", "a": "A retenção ocorre dentro da célula muscular, o que é benéfico para o volume e força, não causando inchaço subcutâneo se a dieta estiver correta."}
        ]
    },
    'MLB15238956': {
        'intro': "A Chapinha MQ Professional Titanium Pro 480 é a ferramenta definitiva para profissionais da beleza. Projetada para suportar o uso contínuo em salões, ela entrega resultados de alisamento perfeitos com rapidez e segurança para os fios.",
        'features': "Equipada com placas de titânio ultra lisas, ela mantém a temperatura estável em até 480°F (250°C). Possui tecnologia iônica para reduzir o frizz e cabo giratório de 3 metros para total mobilidade.",
        'pros': "Aquecimento ultra rápido; Placas de titânio duráveis; Ideal para processos químicos como progressivas; Bivolt automático.",
        'cons': "Temperatura muito alta requer cuidado extremo para não danificar fios sensíveis; Preço de investimento profissional.",
        'target': "Cabeleireiros profissionais e usuários exigentes que buscam um alisamento de nível de salão em casa com durabilidade.",
        'comparison': "Supera modelos domésticos comuns pela estabilidade de calor e pela capacidade de selar as cutículas de forma muito mais eficiente.",
        'faq': [
            {"q": "Pode ser usada em cabelo úmido?", "a": "Não, recomenda-se o uso apenas em cabelos 100% secos para evitar danos térmicos."},
            {"q": "Qual a temperatura ideal para cabelos finos?", "a": "Para cabelos finos ou fragilizados, recomenda-se usar temperaturas abaixo de 375°F."},
            {"q": "As placas riscam fácil?", "a": "O titânio é muito resistente, mas recomenda-se limpar apenas com pano úmido e macio após o resfriamento."}
        ]
    },
    'MLB24028629': {
        'intro': "O Soundcore by Anker P20i redefine o que esperar de um fone Bluetooth de entrada. Com graves potentes e uma bateria de longa duração, ele é o companheiro ideal para o dia a dia, seja no transporte ou na academia.",
        'features': "Possui drivers de 10mm para som encorpado, Bluetooth 5.3 para conexão estável e resistência à água IPX5. O aplicativo Soundcore permite personalizar o equalizador com 22 predefinições diferentes.",
        'pros': "Bateria de até 30 horas com o estojo; Carregamento rápido (10 min = 2h de som); App de personalização completo; Leve e confortável.",
        'cons': "Não possui cancelamento de ruído ativo (ANC); Estojo de carregamento um pouco volumoso.",
        'target': "Pessoas que buscam um fone confiável, com boa qualidade de som para música e chamadas, sem gastar muito.",
        'comparison': "Oferece uma experiência de software e qualidade de construção muito superior aos fones genéricos da mesma faixa de preço.",
        'faq': [
            {"q": "É bom para praticar esportes?", "a": "Sim, a certificação IPX5 garante resistência ao suor e chuvas leves."},
            {"q": "Funciona de forma independente (só um lado)?", "a": "Sim, você pode usar apenas o fone esquerdo ou o direito enquanto o outro carrega."},
            {"q": "Tem garantia no Brasil?", "a": "A Anker costuma oferecer uma das melhores garantias do mercado para seus produtos oficiais."}
        ]
    },
    'MLB26000295': {
        'intro': "O Barbeador Elétrico Philips Power Adapt S5880/20 combina tecnologia avançada com conforto excepcional. Suas lâminas auto-afiáveis e cabeças flexíveis 360° garantem um barbear rente mesmo em áreas difíceis como o pescoço.",
        'features': "Conta com a tecnologia SkinIQ que ajusta a potência conforme a densidade da barba. É totalmente à prova d'água, permitindo o uso a seco ou com espuma, inclusive debaixo do chuveiro.",
        'pros': "Barbear suave sem irritar a pele; Sensor de densidade de barba; Fácil de limpar (abre com um toque); Bateria de longa duração.",
        'cons': "Custo das cabeças de reposição; Não apara pelos muito longos (ideal para uso frequente).",
        'target': "Homens que buscam praticidade no dia a dia e sofrem com irritação causada por lâminas manuais convencionais.",
        'comparison': "Comparado a modelos mais simples da Philips, a linha 5000 oferece um corte muito mais rápido e um motor mais silencioso e potente.",
        'faq': [
            {"q": "Quanto tempo dura a bateria?", "a": "Uma carga completa oferece cerca de 60 minutos de uso sem fio."},
            {"q": "Pode ser usado ligado na tomada?", "a": "Por segurança (por ser à prova d'água), ele funciona apenas sem fio."},
            {"q": "Com que frequência devo trocar as lâminas?", "a": "A Philips recomenda a troca das cabeças de corte a cada 2 anos para manter o desempenho máximo."}
        ]
    }
}

def expand_all():
    db_path = ROOT / 'data/database/all_products.json'
    with open(db_path, 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    for p in products:
        if p['id'] in PILLAR_CONTENT:
            content = PILLAR_CONTENT[p['id']]
            # Gerar HTML rico para a descrição
            html_content = f"""
            <div class="pillar-content">
                <p class="intro-text">{content['intro']}</p>
                
                <h2>Principais Características</h2>
                <p>{content['features']}</p>
                
                <div class="pros-cons-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 30px 0;">
                    <div class="pros-box" style="background: #f0fdf4; padding: 20px; border-radius: 12px; border-left: 5px solid #22c55e;">
                        <h3 style="margin-top: 0; color: #166534;">✅ Vantagens</h3>
                        <ul>{''.join(f'<li>{item.strip()}</li>' for item in content['pros'].split(';'))}</ul>
                    </div>
                    <div class="cons-box" style="background: #fef2f2; padding: 20px; border-radius: 12px; border-left: 5px solid #ef4444;">
                        <h3 style="margin-top: 0; color: #991b1b;">❌ Desvantagens</h3>
                        <ul>{''.join(f'<li>{item.strip()}</li>' for item in content['cons'].split(';'))}</ul>
                    </div>
                </div>
                
                <h2>Para quem é indicado?</h2>
                <p>{content['target']}</p>
                
                <h2>Comparação com Concorrentes</h2>
                <p>{content['comparison']}</p>
                
                <div class="faq-section" style="margin-top: 40px; background: #f8fafc; padding: 30px; border-radius: 15px;">
                    <h2>Perguntas Frequentes (FAQ)</h2>
                    {''.join(f'<div class="faq-item" style="margin-bottom: 20px;"><strong>Q: {item["q"]}</strong><p style="margin-top: 5px;">A: {item["a"]}</p></div>' for item in content['faq'])}
                </div>
                
                <p style="margin-top: 40px; font-style: italic; color: #64748b;">Nota: Este conteúdo foi gerado com auxílio de inteligência de mercado e curadoria do Compara Preço para garantir a melhor informação antes da sua compra.</p>
            </div>
            """
            p['description'] = html_content
            print(f"✅ Conteúdo expandido para: {p['name']}")
            
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    expand_all()
