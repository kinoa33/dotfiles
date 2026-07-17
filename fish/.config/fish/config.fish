
if status is-interactive
    # Commands to run in interactive sessions can go here
end
fastfetch

function fish_prompt
    echo ""
    set_color green
    echo -n (prompt_pwd) "> "
    set_color normal
end
