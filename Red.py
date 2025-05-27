import discord
from discord.ext import commands, tasks
from discord import app_commands
import random
import logging
import datetime
import os
from dotenv import load_dotenv

#Load .env variables
load_dotenv()
TOKEN = os.getenv('TOKEN')

#Logging setup
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

#Intents setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

#Bot setup
bot = commands.Bot(command_prefix='!', intents=intents)

#Quote list

#Quote list
quotes = [
    "Religious suffering is, at one and the same time, the expression of real suffering and a protest against real suffering. Religion is the sigh of the oppressed creature, the heart of a heartless world, and the soul of soulless conditions. It is the opium of the people.",
    "Private property has made us so stupid and one-sided that an object is only ours when we have it – when it exists for us as capital, or when it is directly possessed, eaten, drunk, worn, inhabited, etc., – in short, when it is used by us. Although private property itself again conceives all these direct realisations of possession only as means of life, and the life which they serve as means is the life of private property – labour and conversion into capital.",
    "The philosophers have only interpreted the world, in various ways; the point, however, is to change it.",
    "As individuals express their life, so they are. What they are, therefore, coincides with their production, both with what they produce and with how they produce. The nature of individuals thus depends on the material conditions determining their production.",
    "Both for the production on a mass scale of this communist consciousness, and for the success of the cause itself, the alteration of men on a mass scale is, necessary, an alteration which can only take place in a practical movement, a revolution; this revolution is necessary, therefore, not only because the ruling class cannot be overthrown in any other way, but also because the class overthrowing it can only in a revolution succeed in ridding itself of all the muck of ages and become fitted to found society anew.",
    "The slave frees himself when, of all the relations of private property, he abolishes only the relation of slavery and thereby becomes a proletarian; the proletarian can free himself only by abolishing private property in general.",
    "What the bourgeoisie therefore produces, above all, are its own grave-diggers. Its fall and the victory of the proletariat are equally inevitable.",
    "We by no means intend to abolish this personal appropriation of the products of labour, an appropriation that is made for the maintenance and reproduction of human life, and that leaves no surplus wherewith to command the labour of others. All that we want to do away with is the miserable character of this appropriation, under which the labourer lives merely to increase capital, and is allowed to live only in so far as the interest of the ruling class requires it.",
    "The mode of production of material life conditions the social, political and intellectual life process in general. It is not the consciousness of men that determines their being, but, on the contrary, their social being that determines their consciousness.",
    "The capitalist mode of production and accumulation, and therefore capitalist private property, have for their fundamental condition the annihilation of self-earned private property; in other words, the expropriation of the laborer.",
    "The political freedoms, the right of assembly and association, and the freedom of the press – those are our weapons. Are we to sit back and abstain while somebody tries to rob us of them? It is said that a political act on our part implies that we accept the exiting state of affairs. On the contrary, so long as this state of affairs offers us the means of protesting against it, our use of these means does not signify that we recognise the prevailing order.",
    "Every step of real movement is more important than a dozen programmes.",
    "Labour is the source of all wealth, the political economists assert. And it really is the source Ð next to nature, which supplies it with the material that it converts into wealth. But it is even infinitely more than this. It is the prime basic condition for all human existence, and this to such an extent that, in a sense, we have to say that labour created man himself.",
    "The revolutionary power which will socialise the instruments of labour taken from the capitalist class, will have to mount guard over the general interests of society served by the socialised industries, and in particular over the interests of those directly engaged in them.",
    "All science would be superfluous if the outward appearance and the essence of things directly coincided.",
    "We must not be like some Christians who sin for six days and go to church on the seventh, but we must speak for the cause daily, and make the men, and especially the women that we meet, come into the ranks to help us.",
    "The division of society into a small, excessively rich class and a large, propertyless class of wage-workers results in a society suffocating from its own superfluity, while the great majority of its members is scarcely, or even not at all, protected from extreme want. This state of affairs becomes daily more absurd and – more unnecessary. It must be abolished, it can be abolished.",
    "Only when the great mass of workers take the keen and dependable weapons of scientific socialism in their own hands, will all the petty-bourgeois inclinations, all the opportunistic currents, come to naught. The movement will then find itself on sure and firm ground. “Quantity will do it.”",
    "If, contrary to all the efforts of our enemies, the modern labor movement marches triumphantly forward, its head raised high, then it owes this first and foremost to its calm understanding of the lawfulness of objective historical development, its understanding that “capitalist society with the inevitability of a natural process creates its own negation, namely, the expropriation of the expropriators, the socialist overturn.” In this, its understanding, the labor movement sees a reliable guarantee of its final victory. And from this same source it draws not only its ability to surge forward but also its patience ; not only strength for action, but also the courage to stand firm and to endure.",
    "War unleashes – at the same time as the reactionary forces of the capitalist world – the generating forces of social revolution which ferment in its depths.",
    "From the moment when the priests use the pulpit as a means of political struggle against the working classes, the workers must fight against the enemies of their rights and their liberation. For he who defends the exploiters and who helps to prolong this present regime of misery, he is the mortal enemy of the proletariat...",
    "Religion is one of the forms of spiritual oppression which everywhere weighs down heavily upon the masses of the people, over burdened by their perpetual work for others, by want and isolation. Impotence of the exploited classes in their struggle against the exploiters just as inevitably gives rise to the belief in a better life after death as impotence of the savage in his battle with nature gives rise to belief in gods, devils, miracles, and the like. Those who toil and live in want all their lives are taught by religion to be submissive and patient while here on earth, and to take comfort in the hope of a heavenly reward. But those who live by the labour of others are taught by religion to practise charity while on earth, thus offering them a very cheap way of justifying their entire existence as exploiters and selling them at a moderate price tickets to well-being in heaven. Religion is opium for the people. Religion is a sort of spiritual booze, in which the slaves of capital drown their human image, their demand for a life more or less worthy of man.",
    "And it is not our object to destroy civilization. We do not desire to “divide up,” as people are in the habit of saying; we do not wish to throw humanity back into barbarism; on the contrary, we desire to lift the whole of humanity to the highest thinkable plane of civilization. We wish every individual without exception to have a share in the means of culture and education according to his capacities and his needs. This is the loftiest ideal that the human race can set before itself; and this ideal is possible today because it is only now that, in consequence of the thousands of years of progress towards civilization and of the tremendous acquisitions which man has gained in this age of culture; because only now are all the means and possibilities given through which we may realize this ideal condition in the way that the majority of men desire to realize it.",
    "Whatever is done we must do ourselves, and if we stand up like men from the Atlantic to the Pacific and from Canada to the Gulf, we will strike terror to their cowardly hearts and they will be but too eager to relax their grip upon our throats and beat a swift retreat.",
    "They have done their best and their worst to crush and enslave us. Their politicians have betrayed us, their courts have thrown us into jail without trial and their soldiers have shot our comrades dead in their tracks.The worm turns at last, and so does the worker.",
    "When, in the course of human development, existing institutions prove inadequate to the needs of man, when they serve merely to enslave, rob, and oppress mankind, the people have the eternal right to rebel against, and overthrow, these institutions.",
    "Capitalism has triumphed all over the world, but this triumph is only the prelude to the triumph of labour over capital.",
    "Unity must be won, and only the workers, the class-conscious workers themselves can win it – by stubborn and persistent effort.",
    "Marx’s economic doctrine is the most profound, comprehensive and detailed confirmation and application of his theory.",
    "There are individuals Ð a mere handful in the history of mankind Ð who, while themselves being the product of an imminent catastrophic change, leave their mark upon an entire epoch. Vladimir Ilyich Lenin is one such giant mind, one such giant will...",
    "The revolution will move forward until its consolidation is total. The time is still far off when there can be a period of relative calm. And life is always revolution.",
    "And so in capitalist society we have a democracy that is curtailed, wretched, false, a democracy only for the rich, for the minority. The dictatorship of the proletariat, the period of transition to communism, will for the first time create democracy for the people, for the majority, along with the necessary suppression of the exploiters, of the minority. Communism alone is capable of providing really complete democracy, and the more complete it is, the sooner it will become unnecessary and wither away of its own accord.",
    "The Communist Manifesto gives a general summary of history, which compels us to regard the state as the organ of class rule and leads us to the inevitable conclusion that the proletariat cannot overthrow the bourgeoisie without first winning political power, without attaining political supremacy, without transforming the state into the “proletariat organized as the ruling class”; and that this proletarian state will begin to wither away immediately after its victory because the state is unnecessary and cannot exist in a society in which there are no class antagonisms.",
    "To work, everybody to work, the cause of the world socialist revolution must and will triumph.",
    "Everybody talks about imperialism. But imperialism is merely monopoly capitalism.",
    "The leaders of the petty bourgeoisie ‘must teach the people to trust the bourgeoisie. The proletarians must teach the people to distrust the bourgeoisie.",
    "It is only in revolutionary struggle against the capitalists of every country, and only in union with the working women and men of the whole world, that we will achieve a new and brighter future-the socialist brotherhood of the workers.",
    "Comrades, just as the earth, after a long drought, pants for rain, so the workers of the world pant for the end of the accursed war, for unification. This striving of the workers for unification is the greatest factor in world history.",
    "Anyone who doubts the inevitability of the dictatorship of the proletariat, as a necessary stage of its victory over the bourgeoisie, facilitates the conditions for the victory of the latter; anyone who doubts or renounces the political party of the proletariat, is helping to weaken and disorganize the working class.",
    "It is folly, not revolutionism, to deprive ourselves in advance of any freedom of action, openly to inform an enemy who is at present better armed than we are whether we shall fight him, and when. To accept battle at a time when it is obviously advantageous to the enemy, but not to us, is criminal; political leaders of the revolutionary class are absolutely useless if they are incapable of “changing tack, or offering conciliation and compromise” in order to take evasive action in a patently disadvantageous battle.",
    "The popular masses who want peace, freedom and bread must, in this period of dark onrush of events, always hold themselves ready to spring up as one man against every danger of new carnage and suffering threatened by the so heroic exploits of fascism.",
    "When wages have disappeared, when all are upon a basis of economic equality, when the position of manager, director, organiser, etc., brings no material advantage, the desire for it will be less widespread and less keen, and the danger of oppressive action by the management will be largely nullified. Nevertheless, management imposed on unwilling subordinates will not be tolerated; where the organiser has chosen the assistants, the assistants will be free to leave, or change him; where the assistants choose the organiser, they will be free to change him. Co-operation for the common good is necessary, but freedom, not domination, is the goal.",
    "The practical task of a reconstruction of society may be correctly solved by the application of a scientific policy of the working class, i.e., a policy based on scientific theory; this scientific theory, in the case of the proletarian, is the theory founded by Karl Marx.",
    "The words Socialism and Communism have the same meaning. They indicate a condition of society in which the wealth of the community: the land and the means of production, distribution and transport are held in common, production being for use and not for profit.",
    "Our object is the economic freedom of the producing classes; this ultimate goal will be attained after a long and bitter struggle; therefore, our primary task is to organize the masses and lead them in the struggle for economic freedom.",
    "All the martyrs of the working class...are victims of the same murderer: international capitalism. And it is always in belief in the liberation of their oppressed brothers, without discrimination as to race or country, that the souls of these martyrs will find supreme consolation. After experiencing these painful lessons, the oppressed people of all countries ought to know on which side their true brothers are, and on which side their enemy.",
    "Revolution! The air is filled with flames and fumes. The shapes of men, seen through the smoke, become distorted and unreal. Promethean supermen, they seem, giants in sin or virtue, Satans or saviours. But, in truth, behind the screen of smoke and flame they are like other men: no larger and no smaller, no better and no worse: all creatures of the same incessant passions, hungers, vanities and fears.",
    "Yes, we must fight, struggle, be ready for defeats and disappointments, but once we have consciously set our feet on the right road, with a clear vision of the task ahead, nothing can daunt us and all causes for pessimism disappear.",
    "...We should try to link our personal lives with the cause for which we struggle, with the cause of building communism.",
    "A revolution is not a dinner party, or writing an essay, or painting a picture, or doing embroidery; it cannot be so refined, so leisurely and gentle, so temperate, kind, courteous, restrained and magnanimous. A revolution is an insurrection, an act of violence by which one class overthrows another.",
    "For us, anti-imperialism does not and cannot constitute, by itself a political program for a mass movement capable of conquering state power. Anti-imperialism, even if it could mobilize the nationalist bourgeoisie and petty bourgeoisie on the side of the worker and peasant masses (and we have already definitively denied this possibility), does not annul class antagonisms nor suppress different class interests.",
    "It takes a loud voice to make the deaf hear...",
    "Workers in the bourgeois countries must fight for equal rights for men and women.",
    "We Communists...stand for the organizational unity of the labor movement; we stand for a great single mass Party of the proletariat.",
    "The seizure of power by armed force, the settlement of the issue by war, is the central task and the highest form of revolution.",
    "We should therefore see ourselves as in need of change and capable of being changed. We should not look upon ourselves as immutable, perfect and sacrosanct, as persons who need not and cannot be changed. When we pose the task of remoulding ourselves in social struggle, we are not demeaning ourselves; the objective laws of social development demand it. Unless we do so, we cannot make progress, or fulfill the task of changing society.",
    "Never become alienated from the masses; learn from them and help them. Lead a collective life, inquire into the concerns of the people around you, study their problems their problems and abide by the rules of discipline",
    "The masses must have their own staunch vanguard which, for its part, must maintain close ties with the widest possible section of the masses. Only thus will the emancipation of the people be possible.",
    "All reactionaries are paper tigers. In appearance, the reactionaries are terrifying, but in reality, they are not so powerful. From a long-term point of view, it is not the reactionaries but the people who are powerful.",
    "Classes struggle, some classes triumph, others are eliminated. Such is history; such is the history of civilization for thousands of years. To interpret history from this viewpoint is historical materialism; standing in opposition to this viewpoint is historical idealism.",
    "We stand firmly for peace and against war. However, if the imperialists insist on unleashing another war, we should not be afraid of it. Our attitude on this question is the same as our attitude towards any disturbance: first, we are against it; second, we are not afraid of it.",
    "No matter how hard the reactionaries try to prevent the advance of the wheel of history, revolution will take place sooner or later and will surely triumph.",
    "If it is now, more than ever before, the duty of every State and its leaders not to permit actions which are capable of jeopardizing universal peace. That applies with all the more force to the leaders of the Great Powers.",
    "And the imperialists? Will they sit with their arms crossed? No! The system they practice is the cause of the evils from which we are suffering, but they will try to obscure the facts with spurious allegations, of which they are masters. They will try to compromise the conference and sow disunity in the camp of the exploited countries by offering them pittances.",
    "There is no small enemy nor insignificant force, because no longer are there isolated peoples.",
    "People of the world, be courageous, and dare to fight, defy difficulties and advance wave upon wave. Then the whole world will belong to the people. Monsters of all kinds shall be destroyed.",
    "Socialism is not spontaneous. It does not arise of itself. It has abiding principles according to which the major means of production and distribution ought to be socialised if exploitation of the many by the few is to be prevented; if, that is to say, egalitarianism in the economy is to be protected.",
    "The urban guerrilla is engaged in revolutionary action for the people, and with them seeks the participation of the people in the struggle against the dictatorship and the liberation of the country.",
    "Historical experience merits attention. A line or a viewpoint must be explained constantly and repeatedly. It won’t do to explain them only to a few people; they must be made known to the broad revolutionary masses.",
    "Ours is the age that can meet the challenge of the times when we work out so new a relationship of theory to practice that the proof of the unity is in the Subject’s own self-development. Philosophy and revolution will first then liberate the innate talents of men and women who will become whole. Whether or not we recognise that this is the task history has “assigned,” to our epoch, it is a task that remains to be done.",
    "We must persist in the mass line: From the masses, to the masses; we must have unshakable faith in the vast majority of the masses and firmly rely on them. Both in revolution and in construction, we should boldly arouse the people and unfold vigorous mass movements.",
    "To remain at home and not vote is behind the political situation. It is insufficient."
]

facts = [
    "The Communist Manifesto was published in 1848 by Karl Marx and Friedrich Engels.",
    "Vladimir Lenin led the Bolshevik Revolution in Russia in 1917.",
    "Che Guevara was an Argentine revolutionary who played a major role in the Cuban Revolution.",
    "The Paris Commune of 1871 is often regarded as the first example of the working class taking power.",
    "The Red Army was established by Leon Trotsky during the Russian Civil War.",
    "Rosa Luxemburg was a Marxist theorist who opposed World War I and was executed in 1919.",
    "The hammer and sickle symbol originated in Soviet Russia and symbolizes the unity of workers and peasants.",
    "Mao Zedong led the Chinese Communist Party to victory in 1949, establishing the People's Republic of China.",
    "The phrase 'dictatorship of the proletariat' describes a transitional socialist state after revolution.",
    "Cuba became a socialist state after the 1959 revolution led by Fidel Castro and Che Guevara."
]


#Slash command
@bot.tree.command(name="quote", description="Get a random communist quote.")
async def quote_command(interaction: discord.Interaction):
    selected = random.choice(quotes)
    await interaction.response.send_message(selected)# Store per-guild daily quote channels
daily_quote_channels = {}

#Slash command: setup daily quotes
@bot.tree.command(name="setdailyquotes", description="Set the channel and optional role for daily quotes.")
@app_commands.describe(channel="The channel for daily quotes", role="Optional role to mention")
@app_commands.checks.has_permissions(administrator=True)
async def set_daily_quotes(interaction: discord.Interaction, channel: discord.TextChannel, role: discord.Role = None):
    guild_id = interaction.guild_id
    daily_quote_channels[guild_id] = {
        "channel_id": channel.id,
        "role_id": role.id if role else None
    }
    await interaction.response.send_message(
        f"✅ Daily quotes will be sent to {channel.mention}" + (f" and mention {role.mention}" if role else "")
    )

#Background task to send daily quote
@bot.tree.command(name="stopdaily", description="Stop daily quotes in this server.")
@app_commands.checks.has_permissions(administrator=True)
async def stop_daily_command(interaction: discord.Interaction):
    guild_id = interaction.guild_id

    if guild_id in daily_quote_channels:
        del daily_quote_channels[guild_id]
        await interaction.response.send_message("🛑 Daily quotes have been stopped for this server.")
    else:
        await interaction.response.send_message("ℹ️ No daily quote is currently set for this server.")

@bot.tree.command(name="stopdaily", description="Stop daily quotes in this server.")
async def stop_daily_command(interaction: discord.Interaction):
    guild_id = interaction.guild_id

    if guild_id in daily_quote_channels:
        del daily_quote_channels[guild_id]
        await interaction.response.send_message("🛑 Daily quotes have been stopped for this server.")
    else:
        await interaction.response.send_message("ℹ️ No daily quote is currently set for this server.")

@bot.tree.command(name="fact", description="Get a random communist or socialist historical fact.")
async def fact_command(interaction: discord.Interaction):
    selected_fact = random.choice(facts)
    await interaction.response.send_message(selected_fact)

#Sync commands & start loop
@bot.event
async def on_ready():
    await bot.tree.sync()
    send_daily_quotes.start()
    print(f"Bot ready as {bot.user}")


# Run bot
bot.run(TOKEN)
